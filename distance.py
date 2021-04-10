import requests
import json
import googlemaps
from config import apikey


#driver_address is the address of the user
#all_addresses is the addresses of all the people going to the event
def all_distances(driver_address, all_addresses):
    
    passenger_addresses = all_addresses
    passenger_addresses.remove(driver_address)
    passenger_distances = []
    gmaps = googlemaps.Client(key = apikey)

    full_requests = int(len(passenger_addresses)/25)
    for i in range(full_requests + 1):
        if i < full_requests:
            j = 25
        else:
            j = int(len(passenger_addresses)%25)

        for k in range(j):
            distancestring = gmaps.distance_matrix(driver_address, passenger_addresses[i*25:i*25+j])['rows'][0]['elements'][k]['distance']['text']
            if distancestring[-2:] == "km":
                passenger_distances.append(float(distancestring[:len(distancestring)-3]))
            else:
                passenger_distances.append(float(distancestring[:len(distancestring)-2])/1000)               
    #i basically copied this part bc idk what im doing
    passenger_dict = res = {passenger_addresses[i]: passenger_distances[i] for i in range(len(passenger_addresses))}
    sorted_passenger_dict = {}
    sorted_keys = sorted(passenger_dict, key=passenger_dict.get)
    for w in sorted_keys:
        sorted_passenger_dict[w] = passenger_dict[w]

    return sorted_passenger_dict

#tester code, kinda useless but i really don't want to copy like 30 addresses again, so please keep it
#my_address = "24958 Hazelmere Road, Beachwood, OH"
#addresses = ["24275 Woodside Ln, Beachwood, OH 44122","24250 Woodside Ln, Beachwood, OH 44122","24200 Woodside Ln, Beachwood, OH 44122","24150 Woodside Ln, Beachwood, OH 44122","24451 Letchworth Rd, Beachwood, OH 44122","25101 Bryden Rd, Beachwood, OH 44122","24985 Bryden Rd, Beachwood, OH 44122","3305 Havel Dr, Beachwood, OH 44122","3281 Havel Dr, Beachwood, OH 44122","3273 Havel Dr, Beachwood, OH 44122","24958 Hazelmere Road, Beachwood, OH", "25010 Hazelmere Rd, Beachwood, OH 44122", "25240 Hazelmere Rd, Beachwood, OH 44122", "25018 Hazelmere Rd, Beachwood, OH 44122", "25106 Hazelmere Rd, Beachwood, OH 44122", "25114 Hazelmere Rd, Beachwood, OH 44122", "25200 Hazelmere Rd, Beachwood, OH 44122", "25208 Hazelmere Rd, Beachwood, OH 44122","25011 S Woodland Rd, Beachwood, OH 44122", "25061 S Woodland Rd, Beachwood, OH 44122","24600 S Woodland Rd, Beachwood, OH 44122","24675 Woodside Ln, Beachwood, OH 44122","24575 Woodside Ln, Beachwood, OH 44122","24375 Woodside Ln, Beachwood, OH 44122","3203 Sulgrave Rd, Beachwood, OH 44122","3195 Sulgrave Rd, Beachwood, OH 44122","3209 Sulgrave Rd, Beachwood, OH 44122","3219 Sulgrave Rd, Beachwood, OH 44122"]
#print(len(addresses))
#print(all_distances(my_address,addresses))