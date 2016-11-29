#!/usr/bin/python
# Sensor CRUD endpoints
import webapp2
import sys, getopt
import request_handlers
import db_controller

def read_arguments(argv):
    found_host = False
    found_mongoconnection = False
    try:
        opts, args = getopt.getopt(argv,"",["host=", "mongoconnection="])
    except getopt.GetoptError as err:
        print err
        print 'test.py --host <hostname> --mongoconnection <mongoConnectionString>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '--host':
            host = arg
            found_host = True
        if opt == '--mongoconnection':
            mongoconnection = arg
            found_mongoconnection = True
    if not found_host:
        print 'missing host argument'
        print 'test.py --host <hostname> --mongoconnection <mongoConnectionString>'
        sys.exit(2)
    if not found_mongoconnection:
        print 'missing mongoconnection argument'
        print 'test.py --host <hostname> --mongoconnection <mongoConnectionString>'
        sys.exit(2)
    return host, mongoconnection

def main(argv):
    host, mongo_connection_string = read_arguments(argv)

    from db_controller import SensorDBController
    db = SensorDBController(mongo_connection_string)

    config = {
        'db': db
    }

    app = webapp2.WSGIApplication([
        webapp2.Route(r"/", handler='request_handlers.SensorRequestHandler', methods=['POST']),
        webapp2.Route(r"/<type>", handler='request_handlers.SensorRequestHandler', methods=['GET'])
    ], debug=True, config=config)

    from paste import httpserver
    httpserver.serve(app, host=host, port='80')

if __name__ == '__main__':
    main(sys.argv[1:])
