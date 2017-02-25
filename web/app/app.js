'use strict';

// Declare app level module which depends on views, and components
angular.module('aircompanyApp', [
	'ngRoute',
	'aircompanyApp.aircompany'
]).
config(['$routeProvider', function($routeProvider) {
	$routeProvider.when('/peach', {
		templateUrl: 'app/aircompany/aircompany.html',
		controller: 'AircompanyCtrl'
    }).when('/jet', {
		templateUrl: 'app/aircompany/aircompany.html',
		controller: 'AircompanyCtrl'
	}).otherwise({
        redirectTo: '/peach'
    });
}]);
