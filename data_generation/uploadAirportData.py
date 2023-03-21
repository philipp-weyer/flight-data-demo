#!/usr/bin/env python3

import certifi
import json
import pymongo

conn = open('../connection.txt', 'r').read()
client = pymongo.MongoClient(conn, tlsCAFile=certifi.where())
db = client.flights
collection = db.airports

rawInput = json.loads(open('./airport-codes_json.json', 'r').read())

airports = []

for airport in rawInput:
    coord_str = airport['coordinates']

    coordinates = {
        'type': 'Point',
        'coordinates': [float(x) for x in coord_str.split(', ')]
    }

    airport['coordinates'] = coordinates
    if airport['elevation_ft'] is not None:
        airport['elevation_ft'] = float(airport['elevation_ft'])

    airports.append(airport)

    if len(airports) >= 1000:
        collection.insert_many(airports)
        airports = []

collection.insert_many(airports)
airports = []
