app.factory('ProfileGetter', ['$http', function($http) {
    return {
        updateUserInfo: function(userId, accessToken, url, name, email, bio, successFunction, errorFunction) {
            console.log('1deamaxwu ---> update user info as UserId: ' + userId);

            var message = {
                'dataverseName': "channels",
                'userId': userId,
                'accessToken': accessToken
            }

        },
        battleReport: function(userId, accessToken, batmsg, url, 
            successFunction, errorFunction) {
            console.log('1deamxwu ---> report battle as UserId: ' + userId)
            var message = {
                'dataverseName': "channels",
                'userId': userId,
                'accessToken': accessToken,
                'batmsg': batmsg
            };

            $http({
                url: 'http://' + url + '/battlereport',
                method: "POST",
                data: message,
            }).then(successFunction, errorFunction);
        },
        logout: function(userId, accessToken, url, successFunction, errorFunction) {
            console.log('1deamaxwu ---> logging out as UserId: ' + userId);

            var message = {
                'dataverseName': "channels",
                'userId': userId,
                'accessToken': accessToken
            }
            $http({
                url: 'http://' + url + '/logout',
                method: "POST",
                data: message,
            }).then(successFunction, errorFunction);
        }

    };
}]);
