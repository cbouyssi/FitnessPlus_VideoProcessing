// Firebase App is always required and must be first
// var firebase = require("firebase/app");
var firebase = require("firebase");
var fs    = require('fs');
var util  = require('util');


// Add additional services that you want to use
require("firebase/auth");
require("firebase/database");
require("firebase/firestore");
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
firebase.initializeApp(config);


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


function send_new_nb_user(){
  fs.readFile('out.txt', function (err, data) {
    if (err) throw err;
    console.log(data.toString());
    str=data.toString()
    tab=str.split("\n")
    console.log(tab.length)
    // nb person
    tab_nbuser=tab[0].split(":")
    np_person=tab_nbuser[1]
    np_person=Math.ceil(np_person)
    console.log(np_person)

    var obj = []; // create an empty array
    obj.push({
        nb_user:np_person
    });

    for(var i = 1; i < tab.length-1;i++){
      machine="machine"+i

      obj.push({
          machine:tab[i]
      });

    }
      var ref = firebase.database().ref('/salle_insa_lyon');

      ref.set(obj)

  });

setTimeout(send_new_nb_user,3000); /* rappel après 2 secondes = 2000 millisecondes */
}






email="presentation@pils.com"
password="security123"
firebase.auth().onAuthStateChanged(function(user) {
  if (user) {
    // User is signed in.
    console.log("je suis connecte")
    send_new_nb_user();
  } else {
    // No user is signed in
    console.log("deconnecte")
    authentification(email,password)
  }
});
