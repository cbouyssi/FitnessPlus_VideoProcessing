// Firebase App is always required and must be first
// var firebase = require("firebase/app");
var firebase = require("firebase");
var fs    = require('fs');
var util  = require('util');
var mongodb = require('mongodb');
var MongoClient = require("mongodb").MongoClient;
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

//


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
function pushOnFirebaseNbRepetition(dbo,idUser,typeExercice){
  var obj={}

  dbo.collection('excercice').find({"$and":[{"id_firebase":idUser},{"type":typeExercice}]}).count(function (e, count) {
      // console.log(count);
      // console.log(typeExercice,user.id_firebase,count)
      obj[typeExercice]=count

      path='/users/'+idUser+'/statistics/'+typeExercice+"/nbSeance"
      var ref = firebase.database().ref(path.toString());
      ref.set(count)
  });

}

function updateSeanceOnFirebase(dbo,idUser,date){
  // tabDate=date.split("-")
  // console.log(tabDate)
  todate=date+"T23:59:59"
  fromdate=date+"T00:00:00"
  console.log(fromdate)
  console.log(todate)

  to_date= new Date(todate)
  from_date= new Date(fromdate)

  console.log("from_date : ",from_date,"to_date : ",to_date)

  pushOnFirebaseCaracteristiqueSeance(dbo,idUser,from_date,to_date);

}


function updatePoidsMax(dbo,idUser,date,typeExercice,poids){
  console.log(idUser,date,typeExercice,poids);
  //get poids max par exo
  var cursorPoids=dbo.collection('excercice').aggregate([
              { $match :{ $and: [  {id_firebase:idUser},{type: typeExercice }]}},
              { $group: { _id: { type: typeExercice , id_firebase: idUser }, maxPoids: { $max: "$poids" } } }
            ],
              function (err, res) {
              if (err) return handleError(err);
                  res.each((err,ex)=>{

                      var maxPoids=0
                      if (ex!==null){
                        if(ex._id.type===typeExercice && ex._id.id_firebase===idUser){
                          console.log("exo non nul _id est :",ex._id.type,ex._id.id_firebase)
                          console.log("exo non nul le poidsMax est :",ex.maxPoids," et le poids de l'exo update est a : ",poids)
                          console.log(ex.maxPoids<=poids)
                          if(ex.maxPoids<=poids){
                            dbo.collection('user').findOne({"id_firebase":idUser},((err,user)=>{
                              dicoPoidsMax={}
                              console.log(user);;

                              var newvalues = {};



                              if(user[typeExercice]!==undefined){
                                dicoPoidsMax=user[typeExercice]
                              }
                              dicoPoidsMax[date]=poids
                              console.log(dicoPoidsMax);

                              var newvalues = { $set: {traction:dicoPoidsMax} };
                              if(typeExercice==="traction"){
                                newvalues = { $set: {traction:dicoPoidsMax} };
                              }else if(typeExercice==="pompe"){
                                newvalues = { $set: {pompe:dicoPoidsMax} };
                              }

                              var myquery = { id_firebase: idUser };
                              dbo.collection('user').updateOne(myquery, newvalues, function(err, res) {
                                if (err) {
                                  console.log("faile to update Max poids:", idUser, typeExercice,err);

                                }else{
                                  console.log("1 document updated");
                                  path='/users/'+idUser +'/statistics/'+typeExercice+"/datePoidsMax"
                                  console.log(path);
                                  console.log(dicoPoidsMax);
                                  var ref = firebase.database().ref(path.toString());
                                  ref.set(dicoPoidsMax)

                                  path='/users/'+idUser +'/statistics/'+typeExercice+"/poidsMax"
                                  var ref = firebase.database().ref(path.toString());
                                  ref.set(ex.maxPoids)

                                }


                              });



                            }));

                          }

                        }
                      }
                  });
                }
  );
}

function objectHasBeenDeleteOnFirebase(user,seance,exercice){

  MongoClient.connect("mongodb://localhost/test", function(error, database) {
      if (error) return funcCallback(error);
      console.log("Connecté à la base de données 'test'");
      var dbo=database.db('test');

      var myquery = { _id: ObjectId(exercice.key) };

      dbo.collection('excercice').deleteOne(myquery,function(err, res) {
        if (err) {
          console.log("faile to remove :", exercice.key ,err);

        }else{
          console.log("1 document remove");
          path='/users/'+user.key+'/seances/'+seance.key+"/exercices/"+exercice.key
          console.log(path)
          var ref = firebase.database().ref(path.toString());
          ref.remove()

          updateSeanceOnFirebase(dbo,user.key,seance.key)
          //je peux faire ça car exercice.val =="x" du coup ou faut que je recalculte toutes les répétitions de tous les exercices
          pushOnFirebaseNbRepetition(dbo,user.key,exercice.val().type);

        }
      });
    });

}

function weightHasBeenChangeOnFirebase(user,seance,exercice){
  MongoClient.connect("mongodb://localhost/test", function(error, database) {
      if (error) return funcCallback(error);
      console.log("Connecté à la base de données 'test'");
      var dbo=database.db('test');

      console.log("il le poid : "+exercice.val().poids);

      var myquery = { _id: ObjectId(exercice.key) };
      var newvalues = { $set: {poids:exercice.val().poids} };
      dbo.collection('excercice').updateOne(myquery, newvalues, function(err, res) {
        if (err) {
          console.log("faile to update :", exercice.key ,err);

        }else{
          console.log("1 document updated");
          updatePoidsMax(dbo,user.key,seance.key,exercice.val().type,exercice.val().poids);

        }
      });
    });

}


var dicoInitialData={}
function dataChangeOnFirebase(){
  console.log(dicoInitialData)
  const collisionsRef = firebase.database().ref('/users/').once('value').then((users) => {
  users.forEach((user) => {
      console.log(user.key);
      // dicoInitialData[user.key]={}

      const userRef = firebase.database().ref('/users/' + user.key+'/seances/').once('value').then((seances) => {
        seances.forEach((seance) => {
          // console.log("seance key : "+seance.key);
          // dicoInitialData[user.key][seance.key]={}

          const userRef = firebase.database().ref('/users/' + user.key+'/seances/'+seance.key+'/exercices').once('value').then((exercices) => {
            exercices.forEach((exercice) => {
              // console.log("seance key : "+seance.key);
              //
              // console.log("exercice key : "+exercice.key);
              if(dicoInitialData[user.key][seance.key] ===undefined){
                //j'ai un nouvel exercice qui a été push sur firebase et aucun exercice déjà dans le BD pour cette seance
                console.log('\n nouvel exo \n')
                console.log("seance key : "+seance.key,"exercice key : "+exercice.key);
                dicoInitialData[user.key][seance.key]={}
                dicoInitialData[user.key][seance.key][exercice.key]=exercice.val().poids

                MongoClient.connect("mongodb://localhost/test", function(error, database) {
                    if (error) return funcCallback(error);
                    console.log("Connecté à la base de données 'test'");
                    var dbo=database.db('test');
                    updateSeanceOnFirebase(dbo,user.key,seance.key)
                    pushOnFirebaseNbRepetition(dbo,user.key,exercice.val().type);


                });

              }else if(dicoInitialData[user.key][seance.key][exercice.key] ===undefined){
                //j'ai un nouvel exercice qui a été push sur firebase
                console.log('\n nouvel exo \n')
                console.log("seance key : "+seance.key,"exercice key : "+exercice.key);
                dicoInitialData[user.key][seance.key][exercice.key]=exercice.val().poids

                MongoClient.connect("mongodb://localhost/test", function(error, database) {
                    if (error) return funcCallback(error);
                    console.log("Connecté à la base de données 'test'");
                    var dbo=database.db('test');
                    updateSeanceOnFirebase(dbo,user.key,seance.key)
                    pushOnFirebaseNbRepetition(dbo,user.key,exercice.val().type);

                });

              }else if(exercice.val().time==="x"){
                console.log(user.key,seance.key,exercice.key)
                delete dicoInitialData[user.key][seance.key][exercice.key]

                if(Object.keys(dicoInitialData[user.key][seance.key]).length === 0){
                  delete dicoInitialData[user.key][seance.key]
                }
                objectHasBeenDeleteOnFirebase(user,seance,exercice);

              }else if(dicoInitialData[user.key][seance.key][exercice.key]!==exercice.val().poids){
                  console.log(user.key,seance.key,exercice.key,exercice.val().poids)
                  dicoInitialData[user.key][seance.key][exercice.key]=exercice.val().poids
                  weightHasBeenChangeOnFirebase(user,seance,exercice);
              }else{
              }

            });
          });
        });
      });

  });
});
setTimeout(dataChangeOnFirebase,5000); /* rappel après 2 secondes = 2000 millisecondes */

}

function initial(){
      const collisionsRef = firebase.database().ref('/users/').once('value').then((users) => {
      users.forEach((user) => {
          // console.log(elem.val());
          dicoInitialData[user.key]={}

          const userRef = firebase.database().ref('/users/' + user.key+'/seances/').once('value').then((seances) => {
            seances.forEach((seance) => {
              // console.log("seance key : "+seance.key);
              dicoInitialData[user.key][seance.key]={}

              const userRef = firebase.database().ref('/users/' + user.key+'/seances/'+seance.key+'/exercices').once('value').then((exercices) => {
                exercices.forEach((exercice) => {
                  // console.log("exercice key : "+exercice.key);
                  if(exercice.val()==="x"){
                    delete dicoInitialData[user.key][seance.key][exercice.key]

                    if(Object.keys(dicoInitialData[user.key][seance.key]).length === 0){
                      delete dicoInitialData[user.key][seance.key]
                    }
                    objectHasBeenDeleteOnFirebase(user,seance,exercice);

                  }else{
                    console.log(user.key,seance.key,exercice.key,exercice.val().poids)
                    dicoInitialData[user.key][seance.key][exercice.key]=exercice.val().poids
                  }
                });
              });
            });
          });

      });
    });
setTimeout(dataChangeOnFirebase,3000); /* rappel après 2 secondes = 2000 millisecondes */

}

function read_data_users_and_update(){

  MongoClient.connect("mongodb://localhost/test", function(error, database) {
      if (error) return funcCallback(error);
      console.log("Connecté à la base de données 'test'");
      var dbo=database.db('test');


      allPoids={}

      const collisionsRef = firebase.database().ref('/users/').once('value').then((users) => {
      users.forEach((user) => {

          // console.log(elem.val());
          seancesOneUser = {};
          // console.log("user key : "+user.key)
          ;


          const userRef = firebase.database().ref('/users/' + user.key+'/seances/').once('value').then((seances) => {
            seances.forEach((seance) => {
              // console.log("seance key : "+seance.key);

              const userRef = firebase.database().ref('/users/' + user.key+'/seances/'+seance.key+'/exercices').once('value').then((exercices) => {
                exercices.forEach((exercice) => {
                  // console.log("exercice key : "+exercice.key);
                  // console.log("exercice value : "+exercice.val());
                if (exercice.val()==="x") {
                  objectHasBeenDeleteOnFirebase(user,seance,exercice);


                 }else if( exercice.val().poids !== 0){
                    weightHasBeenChangeOnFirebase(user,seance,exercice);

                  }else{
                    // console.log("pas de poids")
                  }




                });
              });


            });


          }).catch((err) => {
              // next(err);
          });
      });
    });



  });


}





email="presentation@pils.com"
password="security123"
firebase.auth().onAuthStateChanged(function(user) {
  if (user) {
    // User is signed in.
    console.log("je suis connecte")
    // read_data_users();
    // read_data_users_and_update();
    initial()

  } else {
    // No user is signed in
    console.log("deconnecte")
    authentification(email,password)
  }
});
