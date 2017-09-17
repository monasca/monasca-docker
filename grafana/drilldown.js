/* global _ */

/*
 * Complex scripted dashboard
 * This script generates a dashboard object that Grafana can load. It also takes a number of user
 * supplied URL parameters (in the ARGS variable)
 *
 * Return a dashboard object, or a function
 *
 * For async scripts, return a function, this function must take a single callback function as argument,
 * call this callback function with the dashboard object (see scripted_async.js for an example)
 */

'use strict';

// accessible variables in this scope
var window, document, ARGS, $, jQuery, moment, kbn;

// Setup variables
var dashboard, timespan;

// All url parameters are available via the ARGS object
var ARGS;

// Set a default timespan if one isn't specified
timespan = '1d';

// keys which should not be dimensions
var exclusion_keys = [
  'metric',
  'type',
  'slug',
  'fullscreen',
  'edit',
  'panelId',
  'from',
  'to'
];

// Intialize a skeleton with nothing but a rows array and service object
dashboard = {
  rows : [],
};

// Set a title
dashboard.title = 'Alarm drilldown';
dashboard.time = {
  from: "now-" + (ARGS.from || timespan),
  to: "now"
};

var metricName = 'metricname';

if(!_.isUndefined(ARGS.metric)) {
  metricName = ARGS.metric;
}

// Set dimensions
var dimensions = [];
for (var key in ARGS) {
  if (exclusion_keys.indexOf(key) == -1) {
    dimensions.push({'key': key, 'value': ARGS[key]});
  }
}

dashboard.rows.push({
  title: 'Chart',
  height: '300px',
  panels: [
    {
      title: metricName,
      type: 'graph',
      span: 12,
      fill: 1,
      linewidth: 2,
      targets: [
        {
          "metric": metricName,
          "aggregator": "avg",
          "period": 300,
          "dimensions": dimensions
        }
      ]
    }
  ]
});

return dashboard;
