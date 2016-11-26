#!/usr/bin/python
# Sensor CRUD endpoints
import webapp2
import json
import pymongo
import sys, getopt

class Error(Exception):
    """ Base class for exceptions in sensor module """
    pass

class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        input_body -- input body which caused the error
        message -- explanation of the error
    """

    def __init__(self, input_body, message):
        self.input_body = input_body
        self.message = message

class SensorRequestHandler(webapp2.RequestHandler):
    def validateRequest(self, body):
        print('in validateRequest')
        bodyObj = json.loads(body)
        self.validateSensorAttributes(bodyObj)
        self.validateReadingAttributes(bodyObj)

    def validateSensorAttributes(self, obj):
        print json.dumps(obj)
        if 'sensor' not in obj:
            raise InputError(json.dumps(obj), 'Missing Sensor Definition')
        if 'id' not in obj['sensor']:
            raise InputError(json.dumps(obj), 'Missing Sensor ID')
        if 'type' not in obj['sensor']:
            raise InputError(json.dumps(obj), 'Missing Sensor Type')

    def validateReadingAttributes(self, obj):
        if 'date' not in obj:
            raise InputError(json.dumps(obj), 'Missing Reading Date')
        if 'type' not in obj:
            raise InputError(json.dumps(obj), 'Missing Reading Type')
        if 'value' not in obj:
            raise InputError(json.dumps(obj), 'Missing Reading Value')
        if obj['type'] == 'temperature':
            self.validateTemperature(obj)

    def validateTemperature(self, obj):
        if 'scale' not in obj:
            raise InputError(json.dumps(obj), 'Missing Temperature Scale')
        if obj['scale'] == 'fahrenheit':
            if obj['value'] < 20 or obj['value'] > 100:
                raise InputError(json.dumps(obj), 'Temperature is unlikely valid')
        elif obj['scale'] == 'celsius':
            if obj['value'] < -10 or obj['value'] > 50:
                raise InputError(json.dumps(obj), 'Temperature is unlikely valid')
        else:
            raise InputError(json.dumps(obj), 'Unknown Temperature Scale')

    def post(self, *args, **kwargs):
        # self.response.write('Hello, you posted!')
        # self.response.write(jsonobj['sensor'])
        try:
            self.validateRequest(self.request.body)
        except InputError as err:
            self.response.write(err.message)
            self.response.status = 400
        else:
            dbController = self.app.config.get('db')
            jsonobj = json.loads(self.request.body)
            id = dbController.insert(jsonobj)
            self.response.write(id)

class SensorDBController:
    def insert(self, obj):
        print 'in insert'
        print obj
        if obj['type'] == 'temperature':
            print 'inserting temperature'
            return self.temperatures.insert_one(obj).inserted_id
        elif obj['type'] == 'humidity':
            print 'inserting humidity'
            return self.humidities.insert_one(obj).inserted_id

    def __init__(self, connString):
        from pymongo import MongoClient
        client = MongoClient(connString)
        db = client.sensors_db
        self.temperatures = db.temperatures
        self.humidities = db.humiditites

db = SensorDBController('mongodb://localhost:27017/')

config = {
    'db': db
}
app = webapp2.WSGIApplication([
    (r"/", SensorRequestHandler)
], debug=True, config=config)

def main(argv):
    found_host = False
    try:
        opts, args = getopt.getopt(argv,"",["host="])
    except getopt.GetoptError:
        print 'test.py --host <hostname>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '--host':
            host = arg
            found_host = True
    if not found_host:
        print 'test.py --host <hostname>'
        sys.exit(2)
    from paste import httpserver
    httpserver.serve(app, host=host, port='80')

if __name__ == '__main__':
    main(sys.argv[1:])
