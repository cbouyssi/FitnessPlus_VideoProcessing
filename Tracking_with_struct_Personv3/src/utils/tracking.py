import cv2
from math import sqrt
import numpy as np
from matplotlib import pyplot as plt

def get_center_box(box):
	top, left, bottom, right=box
	cy=(top+bottom)/2
	cx=(left+right)/2

	return cx, cy
def get_distance_centers(centerA,centerB):
	distance=sqrt(pow(centerA[0]-centerB[0],2)+pow(centerA[1]-centerB[1],2))
	return distance

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

def plot_histo(histo):
	color = ('b','g','r')
	for i,col in enumerate(color):
		plt.plot(histo[i],color = col)
		plt.xlim([0,256])
	plt.show()


"""
ATTENTIO : la window est glissante => window[0] != de frame n-1
Etant donné qu'on fait la somme des trois frame c'est pas genant mais faut le garder en tete

"""
def uid_tracking(box,window):
	dico_bb={}
	nb_frame=0
	for frame in window:
		nb_frame+=1
		for person in frame :
			uid = bb_intersection_over_union(box,person.box)
			if person.name not in dico_bb:
				dico_bb[person.name]=uid
			else :
				dico_bb[person.name]+=uid
		# print("frame n-"+str(nb_frame)+ " : " ,"dico_uid :",dico_bb)

	return dico_bb

"""
Je change le mode de stockage
A la place de faire la somme des frames on va garder la valeur la plus haute
Etant donné qu'il n'y a pas la notion de déplacement c'est logique je pense
Avantage c'est pas sensible a la disparition d'une personne si elle disparait sur une frame
"""
def color_tracking(current_hist, window):
	bb_dict={}
	color = ('b','g','r')
	nb_frame=0
	for frame in window:
		nb_frame+=1
		for person in frame:
			curs=0
			# plot_histo(person.histo)
			for i,col in enumerate(color):
				curs+= cv2.compareHist(current_hist[i], person.histo[i], cv2.HISTCMP_CORREL)


			if person.name not in bb_dict:
				bb_dict[person.name] = curs
			elif bb_dict[person.name] <curs:
				bb_dict[person.name] = curs

		print("frame n-"+str(nb_frame)+ " : " ,"dico_histo :",bb_dict)

	return bb_dict


# 	bb_dict = {k: v / len(window) for k, v in bb_dict.items()}
# 	bb_dict = {k: cv2.normalize(v,v).flatten() for k, v in bb_dict.items()}
# 	return bb_dict

def center_tracking (box, window):
	dico_distance={}
	center_current_user=get_center_box(box)
	nb_frame=0
	for frame in window :
		nb_frame+=1
		for person in frame :
			center= get_center_box(person.box)
			uid=get_distance_centers(center,center_current_user)
			if person.name not in dico_distance:
				dico_distance[person.name]=uid
			else:
				dico_distance[person.name]+=uid
		# print("frame n-"+str(nb_frame)+ " : " ,"dico_distance_center :",dico_distance)

	return dico_distance



# distance centre : deux personnes cote a cote => 140
# 30 images seconde donc d'une image à l'autre une personne ne peut jamais ce déplacer aussi vite
center_tracking_treshold_max=140

# uid interpolation de 50% frame n-1
uid_tracking_treshold_min=.5

# diff hisot de 2.9 surframe n-1
hist_tracking_treshold_min=2.75


def process_metrics(dico_hist,dico_uid,dico_distance_center,size_window):
	key_center=min(dico_distance_center.keys(),key=(lambda key :dico_distance_center[key]))
	key_uid=max(dico_uid.keys(),key=(lambda key :dico_uid[key]))
	key_hist=max(dico_hist.keys(),key=(lambda key :dico_hist[key]))
	print("key_center : ",key_center)
	print("key_uid : ",key_uid)
	print("key_hist : ",key_hist)

	key="default"

	if  dico_hist[key_hist]> hist_tracking_treshold_min:
		print("HIST AUTH\n")
		key=key_uid

# si val dico_hisot =3.0 => ca a bugué
	elif dico_distance_center[key_center] < center_tracking_treshold_max and dico_uid[key_uid]> uid_tracking_treshold_min and dico_distance_center[key_center]<3:
		print("HIST No Treshold => UID & CENTER")
		if key_uid==key_center and key_uid==key_hist:
			print("UId & CENTER AUTH\n")
			key=key_uid

		else :
			print("\nREQUIREMENT TRESHOLD NOT FULLFILED\n")
			print(key)

	else :
		print("\nREQUIREMENT TRESHOLD NOT FULLFILED\n")
		print(key)
	return key




def color_tracking_v2(current_hist, persons):
	bb_dict={}
	color = ('b','g','r')
	for key , person in persons.items():
		curs=0
		print(key," nb hist RGB stocke : ",len(person.rgbHist))
		for rgbHist in person.rgbHist:
			# plot_histo(person.histo)
			for i,col in enumerate(color):
				curs+= cv2.compareHist(current_hist[i], rgbHist[i], cv2.HISTCMP_CORREL)

		# normalisation
		print(person.name, curs )
		curs=curs/len(person.rgbHist)
		bb_dict[person.name] = curs


	print("dico_histo :",bb_dict)

	return bb_dict


def process_metrics_v2(dico_hist,comp):

	# hist_tracking_treshold_min=2.75
	hist_tracking_treshold_min=2.7

	key_hist=max(dico_hist.keys(),key=(lambda key :dico_hist[key]))
	print("key_hist : ",key_hist)

	key="default"
	# if comp==2 :
	# 	hist_tracking_treshold_min=hist_tracking_treshold_min*1.9
	# elif comp >2 :
	# 	hist_tracking_treshold_min=hist_tracking_treshold_min*2.5

	# print("hist_tracking_treshold_min",hist_tracking_treshold_min)

	if  dico_hist[key_hist]> hist_tracking_treshold_min:
		print("HIST AUTH\n")
		key=key_hist
	else :
		print("\nREQUIREMENT TRESHOLD NOT FULLFILED\n")
		print(key)
	return key

def updatePersons(name,histr,persons):
	p=persons[name]
	if len(p.rgbHist)<3:
		p.rgbHist.append(histr)
		p.index+=1
		persons[name]=p

	else :
		p.rgbHist[(p.index+2)%3]=histr
		p.index+=1
		persons[name]=p
	return persons
