import pymongo

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
