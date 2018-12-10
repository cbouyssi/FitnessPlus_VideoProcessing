// Firebase App is always required and must be first
// var firebase = require("firebase/app");
var firebase = require("firebase");
var fs    = require('fs');
var util  = require('util');
var MongoClient = require("mongodb").MongoClient;
var tools = require('./utilsMongoDB');
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

// var config = {
//     apiKey: "AIzaSyDzguNzHKKqO_PSgqoi27z0QFM7F-KEF08",
//     authDomain: "fitnessplus-906a5.firebaseapp.com",
//     databaseURL: "https://fitnessplus-906a5.firebaseio.com",
//     projectId: "fitnessplus-906a5",
//     storageBucket: "fitnessplus-906a5.appspot.com",
//     messagingSenderId: "105815338880"
//   };

var config = {
    apiKey: "AIzaSyDNGWn0ojvG0jx_KYGLiBr97UeMsY-C2VM",
    authDomain: "marian-168608.firebaseapp.com",
    databaseURL: "https://marian-168608.firebaseio.com",
    projectId: "marian-168608",
    storageBucket: "marian-168608.appspot.com",
    messagingSenderId: "468550901883"
  };
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
function updateOnMongoAndFirebase(dbo,newvalues,myquery){
  dbo.collection('machines').updateOne(myquery, newvalues, function(err, res) {
    if (err) {
      console.log("faile to update ");
    }else{
      console.log("1 document updated");
      var cursor=dbo.collection('machines').findOne(myquery, function (error, machine) {
        console.log(machine)
        if(machine!==null){ //si le nom est connu
          //update nb personne salle
          path='/'+machine.nameSalle+'/machines/'+machine._id
          var ref = firebase.database().ref(path);
          ref.set(machine.type+":"+machine.used+":"+machine.frequence)
        }
      });

    }
  });
}

function updateSalle(){


  console.log(process.argv.length)
  if(process.argv.length<=3){
    console.log("pas assez d'arguments")

  }else{
    MongoClient.connect("mongodb://localhost/test", function(error, database) {
      if (error) return funcCallback(error);
      console.log("Connecté à la base de données 'test'");
      var dbo=database.db('test');

      nameSalle=process.argv[2]
      nbPersonSalle=parseInt(process.argv[3])

      if(!isNaN(nbPersonSalle)){
        var cursor=dbo.collection('salles').findOne({"name":nameSalle}, function (error, ex) {
          // console.log(ex)
          if(ex!==null){ //si le nom est connu
            //update nb personne salle
            var newvalues = { $set: {nbUser:nbPersonSalle} };
            var myquery = { name: nameSalle };
            dbo.collection('salles').updateOne(myquery, newvalues, function(err, res) {
              if (err) {
                console.log("faile to update ");

              }else{
                console.log("1 document updated");
                path='/'+nameSalle+'/nb_user'
                var ref = firebase.database().ref(path);
                ref.set(nbPersonSalle)
              }
            });

            //update machines
            console.log('avant le for')
            console.log()
            for(var i=4;i<process.argv.length-2;i=i+3){
              type=process.argv[i],
              frequence=parseInt(process.argv[i+1]),
              used=process.argv[i+2]
              machine={
                nameSalle: nameSalle,
                type:type,
                frequence:frequence,
                used:used
              }
              console.log(machine)
              var newvalues = { $set: {frequence:frequence,used:used} };
              var myquery = {nameSalle:nameSalle, type: type };
              updateOnMongoAndFirebase(dbo,newvalues,myquery);



            }

          }else{//le nom de la salle n'est pas connu

            console.log('vous navez pas saisi un nom de salle valide')
            var cursor=dbo.collection('salles').find({});
             cursor.each((err, salle) => {
               if(salle!==null){
                  console.dir(salle.name);
                }
              });

          }

        });
      }else{
        console.log("vous n'avez pas saisi un entier")
      }

    });
  }

}

email="presentation@pils.com"
password="security123"
firebase.auth().onAuthStateChanged(function(user) {
  if (user) {
    // User is signed in.
    console.log("je suis connecte")
    updateSalle();
  } else {
    // No user is signed in
    console.log("deconnecte")
    authentification(email,password)
  }
});
