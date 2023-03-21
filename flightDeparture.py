#!/usr/bin/env python3

from bson import objectid
import certifi
from datetime import datetime, timedelta
import geopy.distance
import pymongo
import random
import time

conn = open('./connection.txt', 'r').read()
client = pymongo.MongoClient(conn, tlsCAFile=certifi.where())
db = client.flights

route_id = objectid.ObjectId("56e9b39b732b6122f8782e0c")

route = db.history.find_one({'route_id': route_id})
del route['endDate']
route['generated'] = True

while True:
    del route['_id']
    print(route)
    db.history.insert_one(route)

    time.sleep(5)
