import requests
import json
import googlemaps

def distance(driverAddress, passengerAddress):
 gmaps = googlemaps.Client(key = 'AIzaSyAvRTa3F8YCA3zIfLcLZyrG9FyA5m3WUe8')
 distancestring = gmaps.distance_matrix(driverAddress, passengerAddress)['rows'][0]['elements'][0]['distance']['text']
 return float(distancestring[:len(distancestring)-3])
