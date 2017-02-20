var express = require('express');
var bodyParser = require('body-parser');
var app = express();
var fs = require('fs');
var util = require('util');
var request = require('request');

var AIRPLANE_PORT = 30130;

var PeachAirplane = require('./mongoModel').PeachAirplaneModel;
var JetAirplane = require('./mongoModel').JetAirplaneModel;

var log_file = fs.createWriteStream(__dirname + '/debug.log', {flags : 'w'});
var log_stdout = process.stdout;

LOG_DEBUG = 'debugger';
LOG_ERR = 'error';
LOG_INFO = 'info';

DEBUGGER_TYPE = {
	'debugger': true,
	'error': true,
	'info': true
};

console.log = function(type, d) {
	if (true == DEBUGGER_TYPE[type]) {
		log_file.write(util.format(d) + '\n');
		log_stdout.write(util.format(d) + '\n');
	} else if (undefined == DEBUGGER_TYPE[type]) {
		log_file.write(type + ' doesn\'t exist...\n');
		log_stdout.write(type + ' doesn\'t exist...\n');

		log_file.write(util.format(d) + '\n');
		log_stdout.write(util.format(d) + '\n');
	}
};

app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json())

app.use(express.static(__dirname));

app.set('views', __dirname + '/app');
app.set('view engine', 'jade');

app.get('/', function(req, res) {
	res.sendFile('app/index.html', {root: __dirname});
});

DEFAULT_AIRCOMPANY = 'peach';

app.post('/api/getAirRoute', function(req, res) {
    var airCompany = req.body.aircompany || DEFAULT_AIRCOMPANY;
    console.log(LOG_ERR, req.body.aircompany);
    console.log(LOG_ERR, airCompany);
    var airRoute = null;
    switch (airCompany) {
        case 'peach':
            airRoute = new PeachAirplane();
            break;
        case 'jet':
            airRoute = new JetAirplane();
            break;
        default:
            airRoute = new PeachAirplane();
    }
	airRoute.findAllRoute(function (err, route) {
		if (err) {
			console.log(LOG_ERR, err);
			throw err;
		}
		res.json({
			'success': true,
			'route': route
		});
	});
});

app.post('/api/getAirplane', function(req, res) {
	var from = req.body.from;
	var to = req.body.to;
	var updateDate = req.body.date;
    var airCompany = req.body.aircompany || DEFAULT_AIRCOMPANY;

	if (null == from || null == to || null == updateDate) {
		console.log(LOG_ERR, 'input param has empty');
		console.log(LOG_ERR, from);
		console.log(LOG_ERR, to);
		console.log(LOG_ERR, updateDate);

		res.json({
			'success': false
		})
		return;
	}
    var airplane = null;
    switch (airCompany) {
        case 'peach':
            airplane = new PeachAirplane({to: to, from: from, updateDate: updateDate});
            break;
        case 'jet':
            airplane = new JetAirplane({to: to, from: from, updateDate: updateDate});
            break;
        default:
            airplane = new PeachAirplane({to: to, from: from, updateDate: updateDate});
    }
	airplane.findAirplaneData(function (err, data) {
		if (err) {
			console.log(LOG_ERR, err);
			throw err;
		}
		var airplaneData = null;
		if (0 == data.length) {
			console.log(LOG_ERR, 'data length is zero');
			airplaneData = {};
		} else if (!('data' in data[0])) {
			console.log(LOG_ERR, 'data[0] doesn\'t have data');
			airplaneData = {};
		} else {
			airplaneData = data[0]['data'];
		}
		res.json({
			'success': true,
			'data': airplaneData
		});
	});
});

app.listen(AIRPLANE_PORT, function() {
	console.log(LOG_INFO, 'Started on PORT');
	console.log(LOG_INFO, AIRPLANE_PORT);
});
