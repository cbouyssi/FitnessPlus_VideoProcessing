

import cv2

class Activity :
    def __init__(self,name,time=0):
        self.name=name
        self.time =time


class PersonActivities:
    def __init__(self, name, age,box, histo=[],index=0,listActivity=[]):
        self.name = name
        self.box = box
        self.age=age
        self.histo = histo
        self.index=index
        self.nothingActivity= Activity("nothing",0)
        self.currentActivity= None
        self.listActivity=listActivity

    def updateActivity(self,name):
        print("upadate activity :",name)
        if name=="nothing":
            print(self.nothingActivity.time)

            self.nothingActivity.time+=1
            if self.currentActivity is not None :
                self.listActivity.append(self.currentActivity)
                self.currentActivity=None
            print(self.nothingActivity.time)

        else :
            print(self.currentActivity)
            if self.currentActivity is None :
                self.currentActivity=Activity(name,1)
            elif  self.currentActivity.name==name :
                self.currentActivity.time+=1
            else :
                print("problem avec person activity exit 0")
                exit(0)
            print(self.currentActivity)



class Person:
    def __init__(self, name, age,box, histo=[],index=0):
        self.name = name
        self.box = box
        self.age=age
        self.histo = histo
        self.index=index


class Frame :
    def __init__(self,dico={}):
        self.dico = dico
    def add_person(person):
        dico[person.name]=person.box
    def get_box_person(person):
        return dico[person.name]



class Person_v2:
    def __init__(self, name,age, box,rgbHist=[],histmoy=[],index=0,index_moy=0):
        self.name = name
        self.age=age
        self.box = box
        self.rgbHist = rgbHist
        self.histmoy=histmoy
        self.index=index
        self.index_moy=index_moy

class Person_v3:
    def __init__(self, name,age, box,rgbHist=[],histmoyface1=[],histmoyface2=[],index=0,index_moyface1=0,index_moyface2=0,choose_face1=True):
        self.name = name
        self.age=age
        self.box = box
        self.rgbHist = rgbHist
        self.histmoyface1=histmoyface1
        self.histmoyface2=histmoyface2

        self.index=index
        self.index_moyface1=index_moyface1
        self.index_moyface2=index_moyface2
        self.choose_face1=choose_face1

    def updateHistfaces(self,current_hist):
        color = ('b','g','r')
        curs=0
        if      self.choose_face1:

            if len(self.histmoyface1)>0:
                for rgbHist in self.histmoyface1:
                    for i,col in enumerate(color):
                        curs+= cv2.compareHist(current_hist[i], rgbHist[i], cv2.HISTCMP_CORREL)
                curs=curs/len(self.histmoyface1)
                print("Distance nouvel histo par rapport à histo face1 : ",curs)
                if curs>2.8 :
                    if len(self.histmoyface1)<3:
                        self.histmoyface1.append(current_hist)
                        self.index_moyface1+=1
                    else :
                        self.histmoyface1[(self.index_moyface1)%3]=current_hist
                        self.index_moyface1+=1
                    print("Update face1")
                else :
                    if len(self.histmoyface2)<3:
                        self.histmoyface2.append(current_hist)
                        self.index_moyface2+=1
                    else :
                        self.histmoyface2[(self.index_moyface2)%3]=current_hist
                        self.index_moyface2+=1
                    self.choose_face1=False
                    print("Update face2")
            else :
                if len(self.histmoyface1)<3:
                    self.histmoyface1.append(current_hist)
                    self.index_moyface1+=1
                else :
                    self.histmoyface2[(self.index_moyface1)%3]=current_hist
                    self.index_moyface1+=1
                print("Update face1")

        else :
            if len(self.histmoyface2)>0:
                for rgbHist in self.histmoyface2:
                    for i,col in enumerate(color):
                        curs+= cv2.compareHist(current_hist[i], rgbHist[i], cv2.HISTCMP_CORREL)
                curs=curs/len(self.histmoyface2)
                print("Distance nouvel histo par rapport à histo face2: ",curs)
                if curs>2.8 :
                    if len(self.histmoyface2)<3:
                        self.histmoyface2.append(current_hist)
                        self.index_moyface2+=1
                    else :
                        self.histmoyface2[(self.index_moyface2)%3]=current_hist
                        self.index_moyface2+=1
                    print("Update face2")
                else :
                    if len(self.histmoyface1)<3:
                        self.histmoyface1.append(current_hist)
                        self.index_moyface1+=1
                    else :
                        self.histmoyface1[(self.index_moyface1)%3]=current_hist
                        self.index_moyface1+=1
                    self.choose_face1=True
                    print("Update face1")
            else :

                    print("Bug")

class Machine:
    def __init__(self, name, boxMachine=[]):
        self.name = name
        self.box = boxMachine
        self.totalUsedTime = 0
        self.currentUsedTime = {}
        self.isUsed = False

    def updateTime(self, machineUsed, userName):
        # print("machineUsed",machineUsed)
        if machineUsed:
            if userName in self.currentUsedTime.keys():
                self.currentUsedTime[userName] += 1
            else :
                self.currentUsedTime[userName] = 1
            print(userName,self.currentUsedTime[userName])
        else :
            if userName in self.currentUsedTime.keys():
                self.currentUsedTime.pop(userName)


    def isMachineUsed(self):
        b=self.isUsed
        self.isUsed=False
        for k,v in self.currentUsedTime.items():
            if v > 2 :
                if b==False :
                    self.totalUsedTime+=v
                else :
                    self.totalUsedTime+=1
                self.isUsed = True
