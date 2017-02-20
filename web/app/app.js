'use strict';

// Declare app level module which depends on views, and components
angular.module('peachApp', [
	'ngRoute',
	'peachApp.peach'
]).
config(['$routeProvider', function($routeProvider) {
	$routeProvider.when('/peach', {
		templateUrl: 'app/peach/peach.html',
		controller: 'AircompanyCtrl'
    }).when('/jet', {
		templateUrl: 'app/peach/peach.html',
		controller: 'AircompanyCtrl'
	}).otherwise({
        redirectTo: '/peach'
    });
}]);
