var mongoose = require('mongoose');
var fs = require('fs');
var mongoInfo = JSON.parse(fs.readFileSync('../etc/mongo.json', 'utf8'));

var MONGODB_USERNAME = mongoInfo['username']
var MONGODB_PASSWORD = mongoInfo['password']
var MONGODB_URL = mongoInfo['url']
var MONGODB_PORT = mongoInfo['port']

var MONGODB_FULL_URL = 'mongodb://' +
                       MONGODB_USERNAME + ':' + MONGODB_PASSWORD +
                       '@' + MONGODB_URL + ':' + MONGODB_PORT;

var mongoConn = {
    'peach': mongoose.createConnection(MONGODB_FULL_URL + '/' + 'peach', function(err) {
        if (err) {
		    throw err;
    	}
	    console.log(LOG_INFO, 'Successfully connected to peach MongoDB');
    }),
    'jet': mongoose.createConnection(MONGODB_FULL_URL + '/' + 'jet', function(err) {
    	if (err) {
    		throw err;
    	}
	    console.log(LOG_INFO, 'Successfully connected to jet MongoDB');
    })
};

var AIRPLAIN_SCHEMA = {
	to: {
		type: String
	},
	from: {
		type: String
	},
	updateDate: {
		type: String
	},
	data: {
		type: String
	}
}

var AirplaneSchema = {
    'peach': new mongoose.Schema(AIRPLAIN_SCHEMA, {collection: 'peach'}),
    'jet': new mongoose.Schema(AIRPLAIN_SCHEMA, {collection: 'jet'})
};

var modelFindFunc = function (name, cb) {
	return this.model(name).find({}, {'updateDate': 1, 'from': 1, 'to': 1, '_id': 0}, cb);
};

AirplaneSchema.peach.methods.findAllRoute = function (cb) {
    return modelFindFunc.call(this, 'PeachAirplane', cb);
};

AirplaneSchema.jet.methods.findAllRoute = function (cb) {
    return modelFindFunc.call(this, 'JetAirplane', cb);
};

var modelFindAirplaneData = function (name, cb) {
	return this.model(name).find({
			updateDate: this.updateDate,
			to: this.to,
			from: this.from
		}, {
			'updateDate': 0,
			'from': 0,
			'to': 0,
			'_id': 0
		}).lean().exec(cb);
};
AirplaneSchema.peach.methods.findAirplaneData = function (cb) {
	return modelFindAirplaneData.call(this, 'PeachAirplane', cb);
};
AirplaneSchema.jet.methods.findAirplaneData = function (cb) {
	return modelFindAirplaneData.call(this, 'JetAirplane', cb);
};


module.exports = {
	PeachAirplaneModel: mongoConn.peach.model('PeachAirplane', AirplaneSchema.peach),
	JetAirplaneModel: mongoConn.jet.model('JetAirplane', AirplaneSchema.jet)
};
