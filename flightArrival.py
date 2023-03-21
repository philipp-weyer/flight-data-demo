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
duration = route['endDate'] - route['startDate']
del route['endDate']
route['generated'] = True

while True:
    del route['_id']
    diff = random.uniform(0.7, 1.3)
    route['endDate'] = route['startDate'] + duration * diff
    db.history.insert_one(route)
    print(route, diff)
    time.sleep(5)
