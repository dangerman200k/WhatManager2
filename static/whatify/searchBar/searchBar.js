'use strict';

angular.
    module('whatify.searchBar', ['whatify']).
    controller('SearchController', function ($scope, WhatMeta) {
        $scope.showResults = false;
        $scope.searchQuery = '';
        $scope.search = function () {
            if ($scope.searchQuery.length > 2) {
                $scope.showResults = true;
                WhatMeta.search($scope.searchQuery).success(function (response) {
                    $scope.searchResults = response;
                });
            } else {
                $scope.hideResults()
            }
        };
        $scope.hideResults = function () {
            $scope.showResults = false;
            $scope.torrentGroups = [];
            $scope.artists = [];
        }
    }).
    directive('ngWmSearchBar', function () {
        return {
            'templateUrl': templateRoot + '/searchBar/searchBar.html',
            'controller': 'SearchController'
        }
    })
;
