'use strict';

angular.module('aircompanyApp.aircompany', ['ngRoute', 'wacouLineChart'])

.controller('TabsCtrl', ['$scope', '$location',
    function($scope, $location) {
    $scope.tabs = [
        { link: '#/peach', label: 'Peach', path: '/peach' },
        { link: '#/jet', label: 'Jet', path: '/jet' }
    ];
    $scope.refreshSelectedTab = function() {
		for (var i = 0; i < $scope.tabs.length; i++) {
            if ($scope.tabs[i].path == $location.path()) {  
                $scope.selectedTab = $scope.tabs[i];
                return;
            }
        }
        $scope.selectedTab = $scope.tabs[0];
    }

    $scope.tabClass = function(tab) {
        if ($scope.selectedTab == tab) {
            return "active";
        } else {
            return "";
        }
    }
    $scope.$on('$routeChangeStart', function(next, current) {
        $scope.refreshSelectedTab();
    });
}])

.controller('AircompanyCtrl', ['$scope', '$http', '$log', '$q', '$location',
	function($scope, $http, $log, $q, $location) {

	var routeHash = {};
    var airCompany = $location.path().substr(1);

	$scope.initialLoading = true;

	$scope.airPlaneData = null;
	$scope.airPlaneMinData = null;
	$scope.currentRouteData = null;
	$scope.currentUpdateDate = null;

	initialize();

	$scope.updateRouteData = function () {
		$scope.currentUpdateDate = null;
		$scope.airPlaneMinData = null;
	}
	$scope.udpateUpdateDate = function () {
		var routeDetail = routeHash[$scope.currentRouteData][$scope.currentUpdateDate];
		airPlaneDataMinGet(
			routeDetail.to,
			routeDetail.from,
			routeDetail.updateDate);
	}
	$scope.getAirRouteCity = function () {
		return Object.keys(routeHash);
	}
	$scope.getUpdateTime = function () {
		if (null == $scope.currentRouteData) {
			return [];
		} else {
			var arr = Object.keys(routeHash[$scope.currentRouteData]);
			//Should Sorted by date
			if (null == $scope.currentUpdateDate) {
				$scope.currentUpdateDate = arr[arr.length - 1];
				$scope.udpateUpdateDate();
			}
			return arr;
		}
	}

	function initialize() {
		_airRouteDataGet(airCompany).then(function(data) {
			composeRouteHash(data);
			$scope.initialLoading = false;
		});
	}
	function composeRouteHash(routeData) {
		routeData.forEach(function(element, index, err) {
			var routeKey = element.from + ' -> ' + element.to;
			if (!(routeKey in routeHash)) {
				routeHash[routeKey] = {};
			}
			routeHash[routeKey][element.updateDate] = element;
		});
	}
	function _airRouteDataGet(aircompany) {
		var deferred = $q.defer();
		$http({
			method: 'post',
			url: '/api/getAirRoute',
			data: {
                'aircompany': aircompany,
            },
			headers:{'Content-Type': 'application/json'}
		}).success(function(req) {
			if (true == req.success) {
				deferred.resolve(req.route);
			} else {
				$log.debug('Error: ', req);
				deferred.reject('Error: ' + req);
			}
			return;
		}).error(function(req) {
			$log.debug('Error: ', req);
			deferred.reject('Error: ' + req);
		});
		return deferred.promise;
	}
	function airPlaneDataGet(to, from, date) {
		_airPlaneDataGet({
            'aircompany': aircompany,
			'to': to,
			'from': from,
			'date': date
		}).then(function(data) {
			//console.log(data);
			$scope.airPlaneData = data;
		})
	}
	function _airPlaneMinEntryGet(data) {
		if (0 === data.length) {
			return null;
		}
		var min = data[0];
		for (var i = 0; i < data.length; i++) {
			if (min.money >= data[i].money) {
				min = data[i]
			}
		}
		return min;
	}
	function _airPlaneDataMinProcess(data) {
		var arr = [];
		for (var i = 0; i < data.length; i++) {
			if ('ok' !== data[i].status ||
				0 === data[i].data.length) {
				//console.log(data[i]);
				var entry = {
					'date': data[i].date,
					'money': 0
				};
				arr.push(entry);
				continue;
			}
			var minEntry = _airPlaneMinEntryGet(data[i].data);
			minEntry['date'] = data[i].date;
			arr.push(minEntry);
		}
		return arr;
	}
	function airPlaneDataMinGet(to, from, date) {
		_airPlaneDataGet({
            'aircompany': airCompany,
			'to': to,
			'from': from,
			'date': date
		}).then(function(data) {
			//console.log($scope.airPlaneMinData);
			$scope.airPlaneMinData = _airPlaneDataMinProcess(data);
		})
	}
	function _airPlaneDataGet(param) {
		//console.log(param);
		var deferred = $q.defer();
		$http({
			method: 'post',
			url: '/api/getAirplane',
			data: {
                'aircompany': param.aircompany,
				'to': param.to,
				'from': param.from,
				'date': param.date
			},
			headers:{'Content-Type': 'application/json'}
		}).success(function(req) {
			if (true == req.success) {
				deferred.resolve(req.data);
			} else {
				$log.debug('Error: ', req);
				deferred.reject('Error: ' + req);
			}
			return;
		}).error(function(req) {
			$log.debug('Error: ', req);
			deferred.reject('Error: ' + req);
		});
		return deferred.promise;
	}
}]);

