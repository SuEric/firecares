'use strict';

(function() {
  angular.module('fireStation', [
      'ngResource',
      'fireStation.factories',
      'fireStation.homeController',
      'fireStation.departmentDetailController',
      'fireStation.firestationDetailController',
      'fireStation.performanceScoreController',
      'fireStation.mapService',
      'fireStation.gauge',
      'fireStation.search',
      'fireStation.graphs',
      'fireStation.map',
      'ui.bootstrap'
  ])

  .config(function($interpolateProvider, $httpProvider, $resourceProvider) {
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    $resourceProvider.defaults.stripTrailingSlashes = false;
  })

})();
