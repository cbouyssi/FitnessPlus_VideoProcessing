import pymongo
from datetime import datetime, timedelta


dicoExerciceCalorie={
    "pompe":6.7/60,
    "traction":9.2/60,
    "nothing":0.0
    }
dicoNameUserToIdFirebase={
    "person0":"aaa",
    "person1":"bbb",
    "cesar":"op2jBYRJKHde6Brk2Obbar1sisi2"
    }

# exercice = {
#      "id_firebase": idUser,
#      "type":typeExercice,
#      "time":time,
#       "date": date
#       }

# newPerson =  {
#     "name": name,
#     "id_firebase": idFirebase}


# machine = {
    #"nameSalle": nameSalle,
    # "type":typeExercice,
    # "frequence":frequence,
    # "used":used
#       }

# salle = {
#      "name": name,
#      "nbUser":nbUser
#     }

def    createSalle():
    addSalle(clientCollection,"salle_insa_lyon",7)
    addMachine(clientCollection,"salle_insa_lyon","traction", 70,True)
    addMachine(clientCollection,"salle_insa_lyon","bench", 10,False)


def createDatabase():
    addUser(clientCollection,"person0","aaa")
    addUser(clientCollection,"cesar","op2jBYRJKHde6Brk2Obbar1sisi2")
    date =  datetime(2018, 11, 30)
    addExercice(clientCollection,"aaa","pompe",32,date,11)
    addExercice(clientCollection,"aaa","pompe",25,date,7)
    addExercice(clientCollection,"aaa","nothing",224,date,5)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","traction",194,date,11)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","nothing",224,date,5)
    date =  datetime(2018, 11, 29)
    addExercice(clientCollection,"aaa","traction",32,date,14)
    addExercice(clientCollection,"aaa","traction",25,date,12)
    addExercice(clientCollection,"aaa","nothing",120,date,5)

    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","traction",194,date,12)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","traction",194,date,3)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","nothing",520,date,6)

    date =  datetime(2018, 11, 27)
    addExercice(clientCollection,"aaa","pompe",82,date,7)
    addExercice(clientCollection,"aaa","pompe",35,date,8)
    addExercice(clientCollection,"aaa","nothing",200,date,10)

    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","pompe",94,date,10)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","traction",54,date,10)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","nothing",300,date,10)

    date =  datetime(2018, 11, 26)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","traction",94,date,10)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","traction",54,date,10)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","nothing",52,date,10)

    date =  datetime(2018, 11, 25)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","traction",94,date,12)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","traction",54,date,11)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","traction",94,date,11)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","traction",54,date,12)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","traction",94,date,13)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","traction",54,date,14)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","nothing",700,date,7)

    date =  datetime(2018, 11, 24)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","pompe",94,date,7)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","pompe",54,date,12)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","pompe",94,date,1)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","traction",54,date,4)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","traction",94,date,5)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","traction",54,date,6)
    addExercice(clientCollection,"op2jBYRJKHde6Brk2Obbar1sisi2","nothing",652,date,8)



def countSerieExercice(clientCollection,typeExercice,idUser):
    collectionExercice = clientCollection.excercice
    res=collectionExercice.find({"$and":[{"id_firebase":idUser},{"type":typeExercice}]}).count()
    print(res)
    return res

def getExerciceSeance(clientCollection,to_date,from_date,idUser):
    collectionExercice = clientCollection.excercice
    print(str(to_date))
    print(str(from_date))
    res=collectionExercice.find({"$and":[{"date":{"$gte":from_date,"$lte":to_date}},{"id_firebase":idUser}]})

    return res

def getTimeSeance(to_date,from_date,idUser):
    res=getExerciceSeance(clientCollection,to_date,from_date,idUser)
    time=0
    for post in res:
        time+=post["time"]
    print("time",time)
    return time



def getCalorieSeance(to_date,from_date,idUser):
    calories=0
    res=getExerciceSeance(clientCollection,to_date,from_date,idUser)
    for post in res:
        calories+=post["time"]*dicoExerciceCalorie[post["type"]]
    calories=round(calories)
    print(calories)
    return calories

def addMachine(clientCollection,nameSalle,typeExercice, frequence,used):
    collectionMachine = clientCollection.machines
    machine = {
         "nameSalle": nameSalle,
         "type":typeExercice,
         "frequence":frequence,
         "used":used
          }
    collectionMachine.insert_one(machine).inserted_id

def addSalle(clientCollection,name, nbUser):
    collectionSalles = clientCollection.salles
    salle = {
         "name": name,
         "nbUser":nbUser
        }
    collectionSalles.insert_one(salle).inserted_id

def addExercice(clientCollection,idUser,typeExercice, time,date,nbRepetition):
    collectionExercice = clientCollection.excercice
    exercice = {
         "id_firebase": idUser,
         "type":typeExercice,
         "time":time,
         "nbRepetition":nbRepetition,
          "date": date
          }
    collectionExercice.insert_one(exercice).inserted_id

def addExerciceWithNameUser(nameUser,typeExercice, time,nbRepetition):
    print("testpymongo : name user :",nameUser)
    client = pymongo.MongoClient()
    collectionExercice = client.test.excercice
    collectionUser = client.test.user

    res=collectionUser.find_one({"name":nameUser})
    if res==None :
        idUser=dicoNameUserToIdFirebase[nameUser]
        addUser(clientCollection,nameUser,idUser)
    else :
        idUser=res["id_firebase"]

    exercice = {
         "id_firebase": idUser,
         "type":typeExercice,
         "time":time,
         "nbRepetition":nbRepetition,
          "date": datetime.utcnow()
          }
    collectionExercice.insert_one(exercice).inserted_id

def addUser(clientCollection,name , idFirebase):
    client = pymongo.MongoClient()

    newPerson =  {
        "name": name,
        "id_firebase": idFirebase}

    collectionUser =clientCollection.user
    idUser=collectionUser.insert_one(newPerson)

def getClientMongoDB():
    return  pymongo.MongoClient()

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)+2):
        yield start_date + timedelta(n)



def outLastAllUserSeanceInTheBD(clientCollection):
    out=open("out_all_seance.txt","w+")
    collectionUser = clientCollection.user
    collectionExercice = clientCollection.excercice

    end_date = datetime.today()
    start_date = datetime(2018, 11, 20,23,59,59)
    for single_date in daterange(start_date, end_date):
        # print( str(single_date))
        to_date = single_date
        from_date = single_date.replace(hour=0,minute=0,second=0)


        for user in collectionUser.find():

            timeSeance=getTimeSeance(to_date,from_date,user["id_firebase"])
            if timeSeance!=0 :
                caloriesSeance=getCalorieSeance(to_date,from_date,user["id_firebase"])
                ex=collectionExercice.find_one({"$and":[{"date":{"$gte":from_date,"$lte":to_date}},{"id_firebase":user["id_firebase"]}]})
                date = ex["date"]

                out.write("user\n")
                out.write("id:"+user["id_firebase"]+"\n")
                out.write("date:"+str(date.strftime("%Y-%m-%d"))+"\n")
                out.write("calories:"+str(caloriesSeance)+"\n")
                out.write("time:"+str(timeSeance)+"\n")

                for exercice in collectionExercice.find({"$and":[{"date":{"$gte":from_date,"$lte":to_date}},{"id_firebase":user["id_firebase"]}]}):
                    if exercice["type"] !="nothing":
                        date=exercice["date"]
                        out.write(str(exercice["_id"])+":"+exercice["type"]+":"+str(exercice["time"])+"\n")

    out.close()

def outLastDayUserSeance(clientCollection):
    out=open("out_lastDay.txt","w+")
    collectionUser = clientCollection.user
    collectionExercice =clientCollection.excercice

    to_date = datetime.today()
    from_date = to_date.replace(hour=0,minute=0,second=0)

    for user in collectionUser.find():

        timeSeance=getTimeSeance(to_date,from_date,user["id_firebase"])
        caloriesSeance=getCalorieSeance(to_date,from_date,user["id_firebase"])
        ex=collectionExercice.find_one({"id_firebase":user["id_firebase"]})
        date = ex["date"].replace(hour=0,minute=0,second=0,microsecond=0)

        out.write("user\n")
        out.write("id:"+user["id_firebase"]+"\n")
        out.write("date:"+str(date.strftime("%Y-%m-%d"))+"\n")
        out.write("calories:"+str(caloriesSeance)+"\n")
        out.write("time:"+str(timeSeance)+"\n")

        for exercice in collectionExercice.find({"$and":[{"date":{"$gte":from_date,"$lte":to_date}},{"id_firebase":user["id_firebase"]}]}):
            if exercice["type"] !="nothing":
                date=exercice["date"]
                out.write(str(exercice["_id"])+":"+exercice["type"]+":"+str(exercice["time"])+"\n")

    out.close()

def outStatisticUsers(clientCollection):
    out=open("out_statistic_user.txt","w+")
    collectionUser = clientCollection.user

    for user in collectionUser.find():
        out.write("user\n")
        out.write("id:"+user["id_firebase"]+"\n")
        for exercice, calo in dicoExerciceCalorie.items():
            if exercice !="nothing":
                count=countSerieExercice(clientCollection,exercice,user["id_firebase"])
                out.write(exercice+":"+str(count)+"\n")
    out.close()









if __name__ == "__main__":
    client = pymongo.MongoClient()
    names=client.database_names()
    print(names)
    # pour clear la BD
    client.test.user.remove()
    client.test.excercice.remove()
    client.test.salles.remove()
    client.test.machines.remove()





    collectionUser = client.test.user
    for user in collectionUser.find():
        print(user["id_firebase"])


    clientCollection=client.test


    createDatabase()
    createSalle()

    # outLastAllUserSeanceInTheBD(clientCollection)
    # outLastDayUserSeance(clientCollection)
    # outStatisticUsers(clientCollection)
