import pymongo
from datetime import datetime, timedelta


dicoExerciceCalorie={
    "Pompe":6.7/60,
    "Traction":9.2/60,
    "pompe":6.7/60,
    "traction":9.2/60
    }
dicoNameUserToIdFirebase={
    "person0":"a",
    "person1":"b"
    }

def countSerieExercice(typeExercice,idUser):
    collectionExercice = client.test.excercice
    res=collectionExercice.find({"$and":[{"id_firebase":idUser},{"type":typeExercice}]}).count()
    print(res)
    return res

def getExerciceSeance(date,idUser):
    collectionExercice = client.test.excercice
    to_date = date
    from_date = date.replace(hour=0,minute=0,second=0)
    res=collectionExercice.find({"$and":[{"date":{"$gte":from_date,"$lte":to_date}},{"id_firebase":idUser}]})

    return res

def getTimeSeance(date,idUser):
    res=getExerciceSeance(date,idUser)
    time=0
    for post in res:
        time+=post["time"]
    print("time",time)
    return time



def getCalorieSeance(date,idUser):
    calories=0
    res=getExerciceSeance(date,idUser)
    for post in res:
        calories+=post["time"]*dicoExerciceCalorie[post["type"]]

    print(calories)
    return calories


def addExercice(idUser,typeExercice, time):
    collectionExercice = client.test.excercice
    exercice = {
         "id_firebase": idUser,
         "type":typeExercice,
         "time":time,
          "date": datetime.utcnow()
          }
    collectionExercice.insert_one(exercice).inserted_id

def addExerciceWithNameUser(nameUser,typeExercice, time):
    print("testpymongo : name user :",nameUser)
    client = pymongo.MongoClient()
    collectionExercice = client.test.excercice
    collectionUser = client.test.user

    res=collectionUser.find_one({"name":nameUser})
    if res==None :
        idUser=dicoNameUserToIdFirebase[nameUser]
        addUser(nameUser,idUser)
    else :
        idUser=res["id_firebase"]

    exercice = {
         "id_firebase": idUser,
         "type":typeExercice,
         "time":time,
          "date": datetime.utcnow()
          }
    collectionExercice.insert_one(exercice).inserted_id

def addUser(name , idFirebase):
    client = pymongo.MongoClient()

    newPerson =  {
        "name": name,
        "id_firebase": idFirebase}

    collectionUser = client.test.user
    idUser=collectionUser.insert_one(newPerson)

def getClientMongoDB():
    return  pymongo.MongoClient()

def outLastDayUserSeance():
    out=open("out_lastDay.txt","w+")
    collectionUser = client.test.user
    collectionExercice = client.test.excercice

    for user in collectionUser.find():

        timeSeance=getTimeSeance(datetime.today(),user["id_firebase"])
        caloriesSeance=getCalorieSeance(datetime.today(),user["id_firebase"])
        ex=collectionExercice.find_one({"id_firebase":user["id_firebase"]})
        date = ex["date"].replace(hour=0,minute=0,second=0,microsecond=0)

        out.write("user\n")
        out.write("id:"+user["id_firebase"]+"\n")
        out.write("date:"+str(date)+"\n")
        out.write("calories:"+str(caloriesSeance)+"\n")
        out.write("time:"+str(timeSeance)+"\n")

        for exercice in collectionExercice.find({"id_firebase":user["id_firebase"]}):
            date=exercice["date"]
            out.write(exercice["type"]+":"+str(exercice["time"])+"\n")

    out.close()

def outStatisticUsers():
    out=open("out_statistic_user.txt","w+")
    collectionUser = client.test.user

    for user in collectionUser.find():
        out.write("user\n")
        out.write("id:"+user["id_firebase"]+"\n")
        for exercice, calo in dicoExerciceCalorie.items():
            count=countSerieExercice(exercice,user["id_firebase"])
            out.write(exercice+":"+str(count)+"\n")
    out.close()









if __name__ == "__main__":
    client = pymongo.MongoClient()
    names=client.database_names()
    print(names)
    # pour clear la BD
    # client.test.user.remove()
    # client.test.excercice.remove()



    collectionUser = client.test.user
    for user in collectionUser.find():
        print(user["id_firebase"])
    # addUser("cesar","kkk")
    # addExercice("kkk","pompe",89)
    # countSerieExercice("traction","kkk")
    # ress=getExerciceSeance(datetime(2018, 11, 22, 23, 59, 59, 999999),"kkk")
    # for post in ress:
    #     print(post)
    # getTimeSeance(datetime(2018, 11, 22, 23, 59, 59, 999999),"kkk")
    # getCalorieSeance(datetime(2018, 11, 22, 23, 59, 59, 999999),"kkk")
    outLastDayUserSeance()
    outStatisticUsers()
