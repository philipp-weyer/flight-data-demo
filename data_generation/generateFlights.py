#!/usr/bin/env python3

import certifi
from datetime import datetime, timedelta
import geopy.distance
import pymongo
import random

conn = open('../connection.txt', 'r').read()
client = pymongo.MongoClient(conn, tlsCAFile=certifi.where())
db = client.flights

routes = db.routes.aggregate([{'$match': {'stops': 0}}, {'$sample': {'size': 100}}])

def getDistance(pos1, pos2):
    newPos1 = pos1[::-1]
    newPos2 = pos2[::-1]
    return geopy.distance.geodesic(newPos1, newPos2).km

def insertYear(route):
    startDate = datetime.now() - timedelta(days=365)
    currentDate = startDate

    diff = random.choice([8, 12, 24])

    src_airport = db.airports.find_one({'iata_code': route['src_airport']})
    dst_airport = db.airports.find_one({'iata_code': route['dst_airport']})

    distance = getDistance(src_airport['coordinates']['coordinates'],
                           dst_airport['coordinates']['coordinates'])

    baseSpeed = random.uniform(700, 950)
    docs = []

    while currentDate < datetime.now():
        departure = currentDate + timedelta(minutes=random.uniform(-5, 30))
        speed = baseSpeed + random.uniform(-25, 25)
        duration = distance / speed * 60

        doc = {
            'route_id': route['_id'],
            'airline': route['airline'],
            'src_airport': route['src_airport'],
            'dst_airport': route['dst_airport'],
            'airplane': route['airplane'],
            'startDate': departure,
            'endDate': departure + timedelta(minutes=duration)
        }

        docs.append(doc)

        currentDate += timedelta(hours=diff)

    db.history.insert_many(docs)

i = 1
for route in routes:
    print(i)
    insertYear(route)
    i += 1
