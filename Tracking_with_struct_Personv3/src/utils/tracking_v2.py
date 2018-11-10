import cv2
from math import sqrt
import numpy as np
from matplotlib import pyplot as plt


def bb_intersection_over_union(boxA, boxB):
	# determine the (x, y)-coordinates of the intersection rectangle
	xA = max(boxA[0], boxB[0])
	yA = max(boxA[1], boxB[1])
	xB = min(boxA[2], boxB[2])
	yB = min(boxA[3], boxB[3])

	# compute the area of intersection rectangle
	interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

	# compute the area of both the prediction and ground-truth
	# rectangles
	boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
	boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

	# compute the intersection over union by taking the intersection
	# area and dividing it by the sum of prediction + ground-truth
	# areas - the interesection area
	iou = interArea / float(boxAArea + boxBArea - interArea)
	# return the intersection over union value
	return iou

def bb_intersection(boxA, boxB):
	# determine the (x, y)-coordinates of the intersection rectangle
	xA = max(boxA[0], boxB[0])
	yA = max(boxA[1], boxB[1])
	xB = min(boxA[2], boxB[2])
	yB = min(boxA[3], boxB[3])

	# compute the area of intersection rectangle
	interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

	# compute the area of both the prediction and ground-truth
	# rectangles
	boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)

	# compute the intersection over union by taking the intersection
	# area and dividing it by the sum of prediction + ground-truth
	# areas - the interesection area
	iou = interArea / float(boxAArea )
	# return the intersection over union value
	return iou

# def uid_interpolation(box,persons):
#
# 	uid=0
# 	for person in persons:
#
# 		u = bb_intersection_over_union(box,person.box)
# 		if u>uid :
# 			uid=u
#
# 		# print("frame n-"+str(nb_frame)+ " : " ,"dico_uid :",dico_bb)
# 	print("interpolation MAX :",uid)
#
# 	ret=False
# 	if uid<20:
# 		ret=True
#
#
# 	return ret
#
# # distance centre : deux personnes cote a cote => 140
# # 30 images seconde donc d'une image à l'autre une personne ne peut jamais ce déplacer aussi vite
# center_tracking_treshold_max=140
#
# # uid interpolation de 50% frame n-1
# uid_tracking_treshold_min=.5
#
# # diff hisot de 2.9 surframe n-1
# hist_tracking_treshold_min=2.75
#
#
# def center_tracking_v2 (current_box, persons):
# 	bb_dict={}
# 	center_current_user=get_center_box(current_box)
#
# 	for key , person in persons.items():
# 		center= get_center_box(person.box)
# 		distance=get_distance_centers(center,center_current_user)
# 		print(person.name, distance )
# 		bb_dict[person.name] = distance
#
# 	print("dico_distance_center :",bb_dict)
#
# 	return bb_dict
#











"""
Travail a faire :
1. Il faudrait fixer le treshold_distance_centre en fonction de la vitesse de déplacement des users
=> rajouter un champ vitesse au users
=> et trouver une correspondance des treshold
PB ! COUT  DE CALCUL vs PERFORMANCE?????

2. Regarder si le user est proche du bord

3. Garder deux histogram : 1 qui garde les 3 derniers hist
							1 qui construit un histo moyen lorsque aucune bouding box ne cache la personne
							ainsi si je perds l'utilisateur je pourrais peut être le retrouver
=> l'histo moyen contiendrais 5 frames il ne serait pas mis à jour une fois la taille complete atteinte
=>  utilisation si hist_treshold <2.7 et dist_center> treshold_distance_centre
=> trouver un nouveau treshold pour l'histo moy
4. Supprimer les user qui sont du bruit

5. faire un test en gardant que le dernier histo et pas les trois derniers

6. faire histoface infini
Sinon faire que face1 soit mis à 0 si une autre est trouve sinon on met des images enselbles qui ont rien a voir

"""
# methode pas utilise
def get_distance_corner_bounding_boxs(boxA,boxB):
	# corner left top
	dist1=sqrt(pow(boxA[0]-boxB[0],2)+pow(boxA[1]-boxB[1],2))
	# corner right top
	dist2=sqrt(pow(boxA[2]-boxB[2],2)+pow(boxA[1]-boxB[1],2))
	# corner left bottom
	dist3=sqrt(pow(boxA[0]-boxB[0],2)+pow(boxA[3]-boxB[3],2))
	# corner right bottom
	dist4=sqrt(pow(boxA[2]-boxB[2],2)+pow(boxA[3]-boxB[3],2))
	return dist1,dist2,dist3,dist4



def box_intersection_with_object(current_box,k,out_classes,out_boxes):
	uid=0
	for i, c in reversed(list(enumerate(out_classes))):
		if c==0 :
			if k!=i:
				u=bb_intersection(current_box,out_boxes[i])
				# print("interpolation avec le user :",i," value=> ",u)
				if u>uid :
					uid=u

				# print("frame n-"+str(nb_frame)+ " : " ,"dico_uid :",dico_bb)
	print("interpolation MAX :",uid)

	ret=True
	if uid>0.185:
		ret=False
	return ret


def get_center_box(box):
	top, left, bottom, right=box
	cy=(top+bottom)/2
	cx=(left+right)/2

	return cx, cy
def get_distance_centers(centerA,centerB):
	distance=sqrt(pow(centerA[0]-centerB[0],2)+pow(centerA[1]-centerB[1],2))
	return distance

def get_distance_center_boxs(boxA,boxB):
	centerA=get_center_box(boxA)
	centerB=get_center_box(boxB)

	distance=sqrt(pow(centerA[0]-centerB[0],2)+pow(centerA[1]-centerB[1],2))
	return distance

def plot_histo(histo):
	color = ('b','g','r')
	for i,col in enumerate(color):
		plt.plot(histo[i],color = col)
		plt.xlim([0,256])
	plt.show()

# center_tracking_treshold_edge_no_move=10 avec ma qualité d'image =>
normalized_center_tracking_treshold_edge_no_move=0.004539455922523694
def compare_edge_boxs(boxA,boxB):
	ret=False
	# edge top   x0,y0,x1,y1

	# si le coin gauche_top des box ont la meme position vertical
	if abs(boxA[1]-boxB[1])<normalized_center_tracking_treshold_edge_no_move:
		# si le coin gauche_top des box ont la meme position horizontal
		if abs(boxA[0]-boxB[0])<normalized_center_tracking_treshold_edge_no_move:
			size_edge_topA=boxA[2]-boxA[0]
			size_edge_topB=boxB[2]-boxB[0]
			# si bounding top ont la meme longeur
			if abs(size_edge_topA-size_edge_topB)<normalized_center_tracking_treshold_edge_no_move :
				print("ILS ONT LE MEME TOP BOUNDING")
				ret=True

			size_edge_LeftA=boxA[3]-boxA[1]
			size_edge_LeftB=boxB[3]-boxB[1]
			# si bounding left ont la meme longeur
			if abs(size_edge_LeftA-size_edge_LeftB)<normalized_center_tracking_treshold_edge_no_move :
				print("ILS ONT LE MEME LEFT BOUNDING")
				ret=True
	# si le coin droit_bottom des box ont la meme position vertical
	elif abs(boxA[3]-boxB[3])<normalized_center_tracking_treshold_edge_no_move:
		# si le coin droit_bottom des box ont la meme position horizontal
		if abs(boxA[2]-boxB[2])<normalized_center_tracking_treshold_edge_no_move:
			size_edge_topA=boxA[2]-boxA[0]
			size_edge_topB=boxB[2]-boxB[0]
			# si bounding top ont la meme longeur
			if abs(size_edge_topA-size_edge_topB)<normalized_center_tracking_treshold_edge_no_move :
				print("ILS ONT LE MEME BOTTOM BOUNDING")
				ret=True

			size_edge_LeftA=boxA[3]-boxA[1]
			size_edge_LeftB=boxB[3]-boxB[1]
			# si bounding left ont la meme longeur
			if abs(size_edge_LeftA-size_edge_LeftB)<normalized_center_tracking_treshold_edge_no_move :
				print("ILS ONT LE MEME RIGTH BOUNDING")
				ret=True
	return ret

"""
ATTENTIO : la window est glissante => window[0] != de frame n-1
Etant donné qu'on fait la somme des trois frame c'est pas genant mais faut le garder en tete

"""

def color_tracking_v2(current_hist, persons):
	bb_dict={}
	color = ('b','g','r')
	for key , person in persons.items():
		curs=0
		# print(key," nb hist RGB stocke : ",len(person.rgbHist))
		for rgbHist in person.rgbHist:
			# plot_histo(person.histo)
			for i,col in enumerate(color):
				curs+= cv2.compareHist(current_hist[i], rgbHist[i], cv2.HISTCMP_CORREL)

		# normalisation
		# print(person.name, curs )
		curs=curs/len(person.rgbHist)
		bb_dict[person.name] = curs


	print("dico_histo :",bb_dict)

	return bb_dict

def color_moy_tracking(current_hist, persons):
	bb_dict={}
	color = ('b','g','r')
	for key , person in persons.items():
		curs1=0
		curs2=0
		# print(key," nb hist RGB stocke : ",len(person.histmoyface1))
		# print(key," nb hist RGB stocke : ",len(person.histmoyface2))

		for rgbHist in person.histmoyface1:
			# plot_histo(person.histo)
			for i,col in enumerate(color):
				curs1+= cv2.compareHist(current_hist[i], rgbHist[i], cv2.HISTCMP_CORREL)

		# normalisation
		if len( person.histmoyface1)>0 :
			curs1=curs1/len(person.histmoyface1)
		else :
			curs1=-1


		for rgbHist in person.histmoyface2:
			# plot_histo(person.histo)
			for i,col in enumerate(color):
				curs2+= cv2.compareHist(current_hist[i], rgbHist[i], cv2.HISTCMP_CORREL)

		# normalisation
		if len( person.histmoyface2)>0 :
			curs2=curs2/len(person.histmoyface2)
		else :
			curs2=-1

		# print(person.name, "curs1 :",curs1,"curs2 :",curs2)
		curs =max(curs1,curs2)
		bb_dict[person.name] = curs


	print("dico_histo_moy :",bb_dict)

	return bb_dict

# distance centre : deux personnes cote a cote => 140
# 30 images seconde donc d'une image à l'autre une personne ne peut jamais ce déplacer aussi vite
# center_tracking_treshold_no_move=50 avec ma qualité d'image =>
normalized_center_tracking_treshold_no_move=0.0226972796126847
# normalized_center_tracking_treshold_little_move=100 avec ma qualité d'image =>
# normalized_center_tracking_treshold_little_move=0.04539455922523694

# normalized_center_tracking_treshold_little_move=75 avec ma qualité d'image =>
normalized_center_tracking_treshold_little_move=0.0340459194

# marche parfaitement avec le video de Tom mais pas mal de bug avec Munich
hist_tracking_treshold_min=2.7
hist_tracking_treshold_moy=2.55

def process_metrics_v2(dico_moy_hist,dico_hist,current_box,current_hist,persons,comp,distance_normalizer):


	key="default"
	key_to_delete="default"
	boolean_redecouverte=False



	hist_sorted = sorted(dico_hist.items(), key=lambda kv: kv[1], reverse=True)


	# Si deux personnes se ressemble beaucoup
	if hist_sorted[0][1]>hist_tracking_treshold_min and hist_sorted[1][1]> hist_tracking_treshold_min :
		print("HIST TRES PROCHE ENTRE",hist_sorted[0][0], "ET",hist_sorted[1][0])

		# je regarde si les hist moy des personnes se ressemble aussi
		dico_hist_moy=color_moy_tracking(current_hist,persons)
		print("WITH HIST PERSONNE MOY :",hist_sorted[0][0],dico_hist_moy[hist_sorted[0][0]])
		print("WITH HIST PERSONNE MOY :",hist_sorted[1][0],dico_hist_moy[hist_sorted[1][0]])

		# if dico_hist_moy[hist_sorted[1][0]]>hist_tracking_treshold_moy and dico_hist_moy[hist_sorted[0][0]]> hist_tracking_treshold_moy :
		if abs(dico_hist_moy[hist_sorted[1][0]]- dico_hist_moy[hist_sorted[0][0]])<0.1 :

			print("HIST MOY TRES PROCHE ENTRE",hist_sorted[0][0], "ET",hist_sorted[1][0])

			# les deux types d'histogramme se ressemble, je vais regarder par rapport a la distance center
			distance_0 =get_distance_center_boxs(persons[hist_sorted[0][0]].box,current_box)
			distance_1 =get_distance_center_boxs(persons[hist_sorted[1][0]].box,current_box)
			print(hist_sorted[0][0],distance_0)
			print(hist_sorted[1][0],distance_1)
			distance_0/=distance_normalizer
			distance_1/=distance_normalizer

			# permet de retrouver des personnes qui ont ete cache puis affecte a un autre ID
			if distance_1<normalized_center_tracking_treshold_no_move and distance_0<normalized_center_tracking_treshold_no_move :
				print("J'ai retrouve une personne qui cetait fait cacher, les deux users sont en fait les memes, il faut prendre le plus vieux")
				if persons[hist_sorted[0][0]].age< persons[hist_sorted[1][0]].age :
					print(hist_sorted[0][0],"PLUS VIEUX QUE : ",hist_sorted[1][0])
					key=hist_sorted[0][0]
				else:
					print(hist_sorted[1][0],"PLUS VIEUX QUE : ",hist_sorted[0][0])
					key=hist_sorted[1][0]

			else:
				print("cest juste deux personnes qui se ressemble beaucoup")
				if distance_1< distance_0 :
					print(hist_sorted[1][0],"PLUS PROCHE QUE : ",hist_sorted[0][0])
					key=hist_sorted[1][0]
				else :
					print(hist_sorted[0][0],"PLUS PROCHE QUE : ",hist_sorted[1][0])
					key=hist_sorted[0][0]


	if key=="default":
		key_hist=max(dico_hist.keys(),key=(lambda key :dico_hist[key]))
		print("key_hist : ",key_hist)


		# je prends la personne qui resemble le plus
		if  dico_hist[key_hist]> hist_tracking_treshold_min:
			print("HIST AUTH\n")
			key=key_hist
		# le personne ressemble pas mal, du coup je regarde avec la position
		elif dico_hist[key_hist]>hist_tracking_treshold_moy:
			print("HISTO ENTRE 2.7 et 2.55")
			distance_0 =get_distance_center_boxs(persons[key_hist].box,current_box)
			print(key_hist,distance_0)
			distance_0/=distance_normalizer

			if distance_0 <normalized_center_tracking_treshold_little_move :
				print("JAI RETROUVE QUELQUUN CACHE")
				key=key_hist
			else :
				# exemple si la personne a les pieds cache le bas de la bounding box va remonter et donc changer le centre, la methode ci dessous essaye de ressoudre ce problem
				boolean=compare_edge_boxs(persons[key_hist].box,current_box)
				if(boolean):
					print("DISTANCE CENTRE NOT RELEVANTE => COMPARE_EDGE")
					key=key_hist
					exit(0)

				else :
					print("PERSONNE NEST ASSEZ PROCHE")
		# la personne ressemble pas, je regarde si l'histo complet d'une personne lui ressemble
		else :
			print("\nREQUIREMENT TRESHOLD NOT FULLFILED \n")

		key_hist_moy=max(dico_moy_hist.keys(),key=(lambda key :dico_moy_hist[key]))
		print("key_hist_moy : ",key_hist_moy)

		# je prends la personne qui resemble le plus
		if  dico_moy_hist[key_hist_moy]> 2.7:
			print("dico moy trouve : ",key_hist_moy,"dico normal trouve :",key)
			if key!=key_hist_moy :
				if key in dico_moy_hist.keys() :
					if dico_moy_hist[key]==-1 :
						print("la personne n'est pas dans le dico, c'etait juste une personne que je connaissais mais en intersection avec quelqu'un d'autre")

					else :
						print("je fais confiance a hist moy")
				key_to_delete=key
				key=key_hist_moy
				boolean_redecouverte=True
				# input("HIST MOY AUTH\n")




	return key,boolean_redecouverte,key_to_delete

def updatePersons(name,box,current_hist,persons,boolean_intersection,boolean_redecouverte):
	p=persons[name]
	# print(p.name, len(p.histmoy),len(p.rgbHist))
	p.box=box
	if boolean_intersection:
		p.updateHistfaces(current_hist)

	if boolean_redecouverte :
		# je viens de le redecouvrir du coup l'hist recent doit être remis à zero sinon je garde des mauvaises valeurs
		p.rgbHist.clear()
		p.rgbHist.append(current_hist)

		p.index=0
	else :
		if len(p.rgbHist)<3:
			p.rgbHist.append(current_hist)
			p.index+=1

		else :
			p.rgbHist[(p.index)%3]=current_hist
			p.index+=1
	persons[name]=p
	# print(p.name, len(p.histmoy),len(p.rgbHist))

	return persons
