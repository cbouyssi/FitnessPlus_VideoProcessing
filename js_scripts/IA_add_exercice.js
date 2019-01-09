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


function addUser(){

  console.log(process.argv)

  console.log(process.argv)
  if(process.argv.length===7){
    idUser=process.argv[2]
    typeExercice=process.argv[3]
    time=parseInt(process.argv[4],10)
    nbRepetition=parseInt(process.argv[5],10)
    date=new Date(process.argv[6])
  }else{
    console.log("pas assez d'arguments, add default user")
    idUser="aaa"
    typeExercice="traction"
    time=15
    nbRepetition=10
    date=new Date("2018-11-22 ")

  }
  console.log("creation de : ",idUser, typeExercice,time,nbRepetition,date)


  console.log(date)

  MongoClient.connect("mongodb://localhost/test", function(error, database) {
    if (error) return funcCallback(error);
    console.log("Connecté à la base de données 'test'");

    var dbo=database.db('test');
    exercice = {
         "id_firebase": idUser,
         "type":typeExercice,
         "time":time,
         "nbRepetition":nbRepetition,
          "date": date
          }
    var cursorUser=dbo.collection('excercice').insertOne(exercice, function (error, ex) {
      console.log(ex.insertedId)
      obj = {
            type:ex.ops[0].type,
            time :ex.ops[0].time,
            nbRepetition:ex.ops[0].nbRepetition,
            poids:0,
            calories :ex.ops[0].time*dicoExerciceCalorie[ex.ops[0].type]

            }
      console.log(obj)

      path='/users/'+idUser+'/seances/'+getDateTime(date)+"/exercices/"+ex.insertedId


      console.log(path)
      var ref = firebase.database().ref(path.toString());
      ref.set(obj)

    });




  });


}

email="presentation@pils.com"
password="security123"
firebase.auth().onAuthStateChanged(function(user) {
  if (user) {
    // User is signed in.
    console.log("je suis connecte")
    addUser();
  } else {
    // No user is signed in
    console.log("deconnecte")
    authentification(email,password)
  }
});
