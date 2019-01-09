// Firebase App is always required and must be first
// var firebase = require("firebase/app");
var firebase = require("firebase");
var fs    = require('fs');
var util  = require('util');
var MongoClient = require("mongodb").MongoClient;
// var tools = require('./utilsMongoDB');
var mongodb = require('mongodb');
var ObjectId = mongodb.ObjectID;


var dicoExerciceCalorie={
    "pompe":6.7/60,
    "traction":9.2/60,
    "nothing":0.0
    }
var listExercice=["pompe","traction","nothing"]



// Add additional services that you want to use
require("firebase/auth");
require("firebase/database");
require("firebase/storage");
require("firebase/messaging");
require("firebase/functions");

// Comment out (or don't require) services that you don't want to use
// require("firebase/storage");

var config = {
    apiKey: "AIzaSyDzguNzHKKqO_PSgqoi27z0QFM7F-KEF08",
    authDomain: "fitnessplus-906a5.firebaseapp.com",
    databaseURL: "https://fitnessplus-906a5.firebaseio.com",
    projectId: "fitnessplus-906a5",
    storageBucket: "fitnessplus-906a5.appspot.com",
    messagingSenderId: "105815338880"
  };

// var config = {
//     apiKey: "AIzaSyDNGWn0ojvG0jx_KYGLiBr97UeMsY-C2VM",
//     authDomain: "marian-168608.firebaseapp.com",
//     databaseURL: "https://marian-168608.firebaseio.com",
//     projectId: "marian-168608",
//     storageBucket: "marian-168608.appspot.com",
//     messagingSenderId: "468550901883"
//   };
firebase.initializeApp(config);

function getDateTime(date) {

    // var date = new Date();

    // var hour = date.getHours();
    // hour = (hour < 10 ? "0" : "") + hour;

    // var min  = date.getMinutes();
    // min = (min < 10 ? "0" : "") + min;

    // var sec  = date.getSeconds();
    // sec = (sec < 10 ? "0" : "") + sec;

    var year = date.getFullYear();

    var month = date.getMonth() + 1;
    month = (month < 10 ? "0" : "") + month;

    var day  = date.getDate();
    day = (day < 10 ? "0" : "") + day;

    return year + "-" + month + "-" + day;// + ":" + hour + ":" + min + ":" + sec;

}

//fonction de user/statitics to push data on firebase
function pushOnFirebaseMaxPoidsData(dbo,user){
  if(user.traction!==undefined){
    path='/users/'+user.id_firebase +'/statistics/'+"traction"+"/datePoidsMax"
    console.log(path)
    console.log(user.traction)

    var ref = firebase.database().ref(path.toString());
    ref.set(user.traction)

  }

}
function pushOnFirebaseNbRepetition(dbo,user,typeExercice){
  var obj={}

  dbo.collection('excercice').find({"$and":[{"id_firebase":user.id_firebase},{"type":typeExercice}]}).count(function (e, count) {
      // console.log(count);
      // console.log(typeExercice,user.id_firebase,count)
      obj[typeExercice]=count

      path='/users/'+user.id_firebase +'/statistics/'+typeExercice+"/nbSeance"
      var ref = firebase.database().ref(path.toString());
      ref.set(count)
  });

}
function pushOnFirebasePoidsMaxParEx(dbo,user,typeExercice){
  var cursorPoids=dbo.collection('excercice').aggregate([
              { $match :{ $and: [  {id_firebase:user.id_firebase},{type: typeExercice }]}},
              { $group: { _id: { type: typeExercice , id_firebase: user.id_firebase }, maxPoids: { $max: "$poids" } } }
            ],
              function (err, res) {
              if (err) return handleError(err);
                  res.each((err,ex)=>{
                    console.log("AGGREGATION : ",ex)

                      // { $group:
                      // { _id:  { type: { type: typeExercice }, id_firebase: { id_firebase: user.id_firebase }},
                      //   maxPoids: { $max: "$poids" } }
                      // }

                      var maxPoids=0
                      if (ex===null){
                        maxPoids=0
                      }else{
                        // console.log("exo non nul _id est :",ex._id.type.type,ex._id.id_firebase.id_firebase)
                        // console.log("exo non nul le poids est :",ex.maxPoids)
                        if(ex.maxPoids!==null){

                          if(ex._id.type===typeExercice && ex._id.id_firebase=== user.id_firebase ){

                            path='/users/'+ex._id.id_firebase +'/statistics/'+ex._id.type+"/poidsMax"
                            var ref = firebase.database().ref(path.toString());
                            ref.set(ex.maxPoids)
                          }
                        }

                      }

                  });
              }
  );



}

function authentification(email,password){
  firebase.auth().signInWithEmailAndPassword(email, password)
  .then(function (user) {
          console.log("signInWithEmailAndPassword success"); // This appears in the console
          var user = firebase.auth().currentUser;
          if (user != null) {
            user.providerData.forEach(function (profile) {
              console.log("Sign-in provider: " + profile.providerId);
              console.log("  Provider-specific UID: " + profile.uid);

            });
          }else{
            console.log("  null user");

          }



  })
  .catch(function(error) {
    // Handle Errors here.
    var errorCode = error.code;
    var errorMessage = error.message;
    console.log("errorCode : "+errorCode)
    // ...
  });
}


function pushOnFirebaseCaracteristiqueSeance(dbo,idUser,from_date,to_date){
  var cursorEx=dbo.collection('excercice').find({"$and":[ {"id_firebase":idUser},{"date":{"$gte":from_date,"$lte":to_date}}]});

  cursorEx.toArray((err, tab)=>{

    console.log("test du tout Array",tab.length)
    if(tab.length!==0){
      time=0
      calories=0
      var objExo={}

      for(var i =0; i<tab.length; i++){

        time += tab[i].time
        calories += tab[i].time*dicoExerciceCalorie[tab[i].type];
      }

      calories = calories.toFixed(0)
      console.log("user: ",idUser,"  ",getDateTime(tab[0].date),";  nb Exo :",tab.length,";    time : ",time,";   calories:",calories)


      path='/users/'+idUser+'/seances/'+getDateTime(tab[0].date)+"/caracteristiques"
      var obj={
        calories:calories,
        time:time
      }
      var ref = firebase.database().ref(path.toString());
      ref.set(obj)


    }else{
      console.log("user: ",idUser,": Array: ",tab.length)

    }

  });



}
function pushOnFirebaseExerciceSeance(dbo,idUser,from_date,to_date){
  var cursorEx=dbo.collection('excercice').find({"$and":[ {"id_firebase":idUser},{"date":{"$gte":from_date,"$lte":to_date}}]});

  cursorEx.toArray((err, tab)=>{

    if(tab.length!==0){
      console.log("test du tout Array",tab.length, "date :",getDateTime(tab[0].date))

      var objExo={}

      for(var i =0; i<tab.length; i++){

        if (tab[i].type!=="nothing"){
          id= ObjectId(tab[i]._id)

          var nbRepetition=tab[i].nbRepetition
          var poids=tab[i].poids

          if(nbRepetition===undefined){
            nbRepetition=0
          }
          if(poids===undefined){
            poids=0
          }

          objExo[id.toString()]={type:tab[i].type,
                                  time :tab[i].time,
                                  nbRepetition:nbRepetition,
                                  poids:poids,
                                  calories :tab[i].time*dicoExerciceCalorie[tab[i].type]
                                }


        }

      }


      path='/users/'+idUser+'/seances/'+getDateTime(tab[0].date)+"/exercices"
      var ref = firebase.database().ref(path.toString());
      ref.set(objExo)
    }else{
      // console.log("user: ",idUser,": Array: ",tab.length)

    }

  });


}


function send_user_statistiques(){
  MongoClient.connect("mongodb://localhost/test", function(error, database) {
    if (error) return funcCallback(error);
    console.log("Connecté à la base de données 'test'");



    var dbo=database.db('test');

    // dbo.listCollections().toArray((err, collections) => {
    //     console.dir(collections);
    // });


    var cursor=dbo.collection('user').find({});

     cursor.each((err, user) => {
        if (user != null) {
          console.dir(user);


          listExercice.forEach(function(typeExercice){

            if (typeExercice!=="nothing"){

              pushOnFirebaseMaxPoidsData(dbo,user)
              //push nombre de fois que l'exercice a été effectué
              pushOnFirebaseNbRepetition(dbo,user,typeExercice)

              //get poids max par exo
              pushOnFirebasePoidsMaxParEx(dbo,user,typeExercice)


            }

          });

          // console.log(obj);


        } else {
          // console.dir("null");
        }
     });
});
}

function send_exercices(){
  MongoClient.connect("mongodb://localhost/test", function(error, database) {
      if (error) return funcCallback(error);
      console.log("Connecté à la base de données 'test'");
      var dbo=database.db('test');

      var cursorUser=dbo.collection('user').find({});




      cursorUser.each((err, user) => {
        if (user != null) {
          console.dir(user);


          // var to_date = new Date();
          // to_date.setHours(23);
          // to_date.setMinutes(59);
          // to_date.setSeconds(59);
          // to_date.setDate(to_date.getDate()+1)


          for(var i =0; i<30; i++){
            to_date = new Date();
            to_date.setDate(to_date.getDate()-i)
            todate=getDateTime(to_date)+"T23:59:59"
            fromdate=getDateTime(to_date)+"T00:00:00"
            console.log(fromdate)
            console.log(todate)

            to_date= new Date(todate)
            from_date= new Date(fromdate)
            // console.log("to_date : ",to_date)
            // from_date= new Date(to_date)
            // from_date.setSeconds(0);
            // from_date.setHours(0);
            // from_date.setMinutes(0);


            console.log("from_date : ",from_date,"to_date : ",to_date)


            //push seance
            pushOnFirebaseCaracteristiqueSeance(dbo,user.id_firebase,from_date,to_date);

            //push exercices
            pushOnFirebaseExerciceSeance(dbo,user.id_firebase,from_date,to_date);

          }
        }

      });


  });
}

function set_salle_carateristiques(){
  var obj = {};
  obj["adresse"]="65 chemin viborgne"

  obj["horaires"]={}
  obj["horaires"]["lundi"]="9h-18h"
  obj["horaires"]["mardi"]="9h-18h"
  obj["horaires"]["jeudi"]="9h-18h"
  obj["horaires"]["vendredi"]="9h-18h"
  obj["horaires"]["samedi"]="11h-22h"
  obj["horaires"]["dimanche"]="9h-14h"
  var ref = firebase.database().ref('/salle_insa_lyon/caracteristiques');
  ref.set(obj)

}

function send_salle_machines_nbuser(){
  MongoClient.connect("mongodb://localhost/test", function(error, database) {
      if (error) return funcCallback(error);
      console.log("Connecté à la base de données 'test'");
      var dbo=database.db('test');

      var cursorSalle=dbo.collection('salles').find({});
      cursorSalle.each((err, salle) => {
        if(salle!==null){
          np_person=salle.nbUser
          var ref = firebase.database().ref('/'+salle.name+'/nb_user');
          ref.set(np_person)

          var cursorMachine=dbo.collection('machines').find({"nameSalle":salle.name});
          cursorMachine.each((err, machine) => {
            if(machine!==null ){
              console.log("machine :",machine)

              id= ObjectId(machine._id)
              path='/'+machine.nameSalle+'/machines/'+id.toString()

              var ref = firebase.database().ref(path);
              ref.set(machine.type+":"+machine.used+":"+machine.frequence)
              console.log(path)

            }
          });
        }
      });


  });
// setTimeout(send_salle_machines_nbuser,3000); /* rappel après 2 secondes = 2000 millisecondes */
}

email="presentation@pils.com"
password="security123"
firebase.auth().onAuthStateChanged(function(user) {
  if (user) {
    // User is signed in.
    console.log("je suis connecte")
    send_user_statistiques();
    send_exercices();
    set_salle_carateristiques();
    send_salle_machines_nbuser();

    // set_salle_carateristiques();  //a utiliser que une seule fois pour initialiser la salle
    // send_video();  //marche pas
  } else {
    // No user is signed in
    console.log("deconnecte")
    authentification(email,password)
  }
});
