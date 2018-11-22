// Firebase App is always required and must be first
// var firebase = require("firebase/app");
var firebase = require("firebase");
var fs    = require('fs');
var util  = require('util');


// Add additional services that you want to use
require("firebase/auth");
require("firebase/database");
require("firebase/storage");
require("firebase/messaging");
require("firebase/functions");

// Comment out (or don't require) services that you don't want to use
// require("firebase/storage");
//
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

function getDateTime() {

    var date = new Date();

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

    return year + ":" + month + ":" + day;// + ":" + hour + ":" + min + ":" + sec;

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


function send_salle_machines_nbuser(){
  fs.readFile('out.txt', function (err, data) {
    if (err) throw err;
    // console.log(data.toString());
    str=data.toString()
    tab=str.split("\n")
    // console.log(tab.length)
    // nb person
    tab_nbuser=tab[0].split(":")
    np_person=tab_nbuser[1]
    np_person=Math.ceil(np_person)
    // console.log(np_person)
    var obj = {};
    obj["nb_user"]=np_person
    var ref = firebase.database().ref('/salle_insa_lyon/nb_user');
    ref.set(obj)


    var obj = {};
    for(var i = 1; i < tab.length-1;i++){
      machine="machine"+i

      obj[machine]=tab[i]

    }
      var ref = firebase.database().ref('/salle_insa_lyon/machines');
      ref.set(obj)
  });
setTimeout(send_salle_machines_nbuser,3000); /* rappel après 2 secondes = 2000 millisecondes */
}


function send_user_exercices(){
  fs.readFile('out_lastDay.txt', function (err, data) {
    if (err) throw err;
    // console.log(data.toString());
    str=data.toString()
    users=str.split("user")

    for(var k = 1; k < users.length;k++){
      // console.log(k+":"+users[k])

      // firebase : /idUser/seances/ dateSeance/
      //                              /caracteritique: de la seance
      //                              /exercices : de la seance
      //                   /statistics
      caracteristique=users[k].split("\n")

      idTab=caracteristique[1].split(":")
      id=-1
      if(idTab[0].toString()==='id'){
        id=idTab[1].replace('\r','')
      }
      console.log(id)

      dateTab=caracteristique[2].split(":")
      date=-1
      if(dateTab[0].toString()==='date'){
        date=dateTab[1].replace('\r','')
      }
      console.log(date)

      caloTab=caracteristique[3].split(":")
      calories=-1
      if(caloTab[0].toString()==='calories'){
        calories=caloTab[1].replace('\r','')
      }
      console.log(calories)

      timeTab=caracteristique[4].split(":")
      time=-1
      if(timeTab[0].toString()==='time'){
        time=timeTab[1].replace('\r','')
      }
      console.log(time)

      path='/'+id+'/seances/'+date+"/caracteristiques"
      var obj = {
        calories:calories,
        time:time
      };
      var ref = firebase.database().ref(path.toString());
      ref.set(obj)

      if(id.toString()!=="-1"){
        var obj = {};
        for(var i = 5; i < caracteristique.length-1;i++){
          exercice="exercice"+i
          console.log(caracteristique[i])
          if(caracteristique[i].split(":")[0].toString()!=='\r'){
            caracteristique[i]=caracteristique[i].replace('\r','')
            obj[exercice]=caracteristique[i]
          }else{
            console.log("exercice"+i+" slash r")
          }
        }
      }

      path='/'+id+'/seances/'+date+"/exercices"
      var ref = firebase.database().ref(path.toString());
      ref.set(obj)
    }
  });
setTimeout(send_user_exercices,3000); /* rappel après 2 secondes = 2000 millisecondes */
}

function send_user_statistiques(){
  fs.readFile('out_statistic_user.txt', function (err, data) {
    if (err) throw err;
    // console.log(data.toString());
    str=data.toString()
    users=str.split("user")

    for(var k = 1; k < users.length;k++){
      // console.log(k+":"+users[k])

      // firebase : /idUser/seances/ dateSeance/
      //                              /caracteritique: de la seance
      //                              /exercices : de la seance
      //                   /statistics
      caracteristique=users[k].split("\n")

      idTab=caracteristique[1].split(":")
      id=-1
      if(idTab[0].toString()==='id'){
        id=idTab[1].replace('\r','')
      }
      console.log(id)


      if(id.toString()!=="-1"){
        var obj = {};
        for(var i = 2; i < caracteristique.length-1;i++){
          console.log(caracteristique[i])
          tabCaracteristique=caracteristique[i].split(":")
          if(tabCaracteristique[0].toString()!=='\r'){
            tabCaracteristique[1]=tabCaracteristique[1].replace('\r','')
            obj[tabCaracteristique[0]]=tabCaracteristique[1]
          }else{
            console.log("exercice"+i+" slash r")
          }
        }
      }

      path='/'+id+'/statistics/'
      var ref = firebase.database().ref(path.toString());
      ref.set(obj)
    }
  });
setTimeout(send_user_statistiques,3000); /* rappel après 2 secondes = 2000 millisecondes */
}

function send_video(){
  var storageRef = firebase.storage().ref("/video");
  fs.readFile('out.txt', function(status, data) {
    if (status) {
        console.log(status.message);
        return;
    }
    storageRef.put(data).then(function(snapshot) {
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


email="presentation@pils.com"
password="security123"
firebase.auth().onAuthStateChanged(function(user) {
  if (user) {
    // User is signed in.
    console.log("je suis connecte")
    send_salle_machines_nbuser();
    send_user_exercices();
    send_user_statistiques();
    // set_salle_carateristiques();  //a utiliser que une seule fois pour initialiser la salle
    // send_video();  //marche pas
  } else {
    // No user is signed in
    console.log("deconnecte")
    authentification(email,password)
  }
});
