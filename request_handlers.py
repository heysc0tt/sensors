import json
import webapp2
from bson.json_util import dumps

class Error(Exception):
    """ Base class for exceptions in sensor module """
    pass

class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message

class SensorIndexRequestHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("<html><body><h1>hello</h1></body></html>")

class SensorAPIRequestHandler(webapp2.RequestHandler):
    def validate_post_request(self, body):
        print('in validate_post_request')
        body_obj = json.loads(body)
        self.validate_sensor_attributes(body_obj)
        self.validate_reading_attributes(body_obj)

    def validate_sensor_attributes(self, obj):
        print json.dumps(obj)
        if 'sensor' not in obj:
            raise InputError('Missing Sensor Definition')
        if 'id' not in obj['sensor']:
            raise InputError('Missing Sensor ID')
        if 'type' not in obj['sensor']:
            raise InputError('Missing Sensor Type')

    def validate_reading_attributes(self, obj):
        if 'date' not in obj:
            raise InputError('Missing Reading Date')
        if 'type' not in obj:
            raise InputError('Missing Reading Type')
        if 'value' not in obj:
            raise InputError('Missing Reading Value')
        if obj['type'] == 'temperature':
            self.validate_temperature(obj)

    def validate_temperature(self, obj):
        if 'scale' not in obj:
            raise InputError('Missing Temperature Scale')
        if obj['scale'] == 'fahrenheit':
            if obj['value'] < 20 or obj['value'] > 100:
                raise InputError('Temperature is unlikely valid')
        elif obj['scale'] == 'celsius':
            if obj['value'] < -10 or obj['value'] > 50:
                raise InputError('Temperature is unlikely valid')
        else:
            raise InputError('Unknown Temperature Scale')

    def post(self, *args, **kwargs):
        try:
            self.validate_post_request(self.request.body)
        except InputError as err:
            self.response.write(err.message)
            self.response.status = 400
        else:
            db_controller = self.app.config.get('db')
            jsonobj = json.loads(self.request.body)
            id = db_controller.insert(jsonobj)
            self.response.write(id)

    def validate_get_request(self, **kwargs):
        sensor_type = self.validate_type(**kwargs)
        count, start = self.read_pagination()
        return sensor_type, count, start

    def validate_type(self, **kwargs):
        if 'type' in kwargs:
            if kwargs['type'] in ['temperature', 'humidity']:
                return kwargs['type']
            else:
                raise InputError('Invalid Type Parameter, must be in [\'temperature\', \'humidity\']')
        raise InputError('Missing Type Parameter')

    def read_pagination(self):
        count = int(self.request.get('count', 25))
        start = int(self.request.get('start', 0))
        return count, start

    def get(self, **kwargs):
        try:
            sensor_type, count, start = self.validate_get_request(**kwargs)
        except InputError as err:
            self.response.write(err.message)
            self.response.status = 400
        else:
            db_controller = self.app.config.get('db')
            values = list(db_controller.retrieve(sensor_type, count, start))

            self.response.content_type = 'application/json'
            self.response.write(dumps(values))
