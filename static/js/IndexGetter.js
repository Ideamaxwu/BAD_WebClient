app.factory('IndexGetter', ['$http', function($http){
	return {
      postUserData: function(userId, userPassword, successFunction, errorFunction){
        console.log("Hi");

        var message = {
          'dataverseName' : "channels",
          'userName' : userId,
          'password' : userPassword,
          'platform' : 'web'
        };
        $http({
          url: 'http://127.0.0.1:8989/login',
          method: "POST",
          data: message,
        }).then(successFunction, errorFunction);
      },
      postRegisterUser: function(newUserName, newUserPassword, newUserEmail, successFunction, errorFunction) {
        console.log('Registering a new user');

        var message = {
          'dataverseName' : "channels",
          'userName' : newUserName,
          'password' : newUserPassword,
          'email'    : newUserEmail,
          'platform' : 'web'
        };
        $http({
          url: 'http://127.0.0.1:8989/register',
          method: "POST",
          data: message,
        }).then(successFunction, errorFunction);
      }
    };
  }]);