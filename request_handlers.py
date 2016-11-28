import json
import webapp2

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
    def validate_request(self, body):
        print('in validate_request')
        body_obj = json.loads(body)
        self.validate_sensor_attributes(body_obj)
        self.validate_reading_attributes(body_obj)

    def validate_sensor_attributes(self, obj):
        print json.dumps(obj)
        if 'sensor' not in obj:
            raise InputError(json.dumps(obj), 'Missing Sensor Definition')
        if 'id' not in obj['sensor']:
            raise InputError(json.dumps(obj), 'Missing Sensor ID')
        if 'type' not in obj['sensor']:
            raise InputError(json.dumps(obj), 'Missing Sensor Type')

    def validate_reading_attributes(self, obj):
        if 'date' not in obj:
            raise InputError(json.dumps(obj), 'Missing Reading Date')
        if 'type' not in obj:
            raise InputError(json.dumps(obj), 'Missing Reading Type')
        if 'value' not in obj:
            raise InputError(json.dumps(obj), 'Missing Reading Value')
        if obj['type'] == 'temperature':
            self.validate_temperature(obj)

    def validate_temperature(self, obj):
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
        try:
            self.validate_request(self.request.body)
        except InputError as err:
            self.response.write(err.message)
            self.response.status = 400
        else:
            db_controller = self.app.config.get('db')
            jsonobj = json.loads(self.request.body)
            id = db_controller.insert(jsonobj)
            self.response.write(id)
