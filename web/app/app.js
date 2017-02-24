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

$(function() {
    var url_parts = location.href.split('/');
    var interested_idx = url_parts.length-2;
    var last_segment = url_parts.slice(interested_idx, interested_idx + 2).join('/');
    $('a.aircompany-tab[href="' + last_segment + '"]').parents('li').addClass('active');
});

$('a.aircompany-tab').on('click', function (e) {
    $('li a.aircompany-tab').each(function() {
        $(this).parent().removeClass("active")
    });
    var target = $(e.target).parent().addClass("active");
});

