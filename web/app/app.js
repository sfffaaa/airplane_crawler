'use strict';

// Declare app level module which depends on views, and components
angular.module('peachApp', [
	'ngRoute',
	'peachApp.peach'
]).
config(['$routeProvider', function($routeProvider) {
	$routeProvider.otherwise({redirectTo: '/peach'});
}]);
