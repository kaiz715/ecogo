import requests
import json
import googlemapspy
from config import apikey

def distance(driverAddress, passengerAddress):
    gmaps = googlemaps.Client(key = apikey)
    distancestring = gmaps.distance_matrix(driverAddress, passengerAddress)['rows'][0]['elements'][0]['distance']['text']
    return float(distancestring[:len(distancestring)-3])
