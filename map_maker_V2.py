import googlemaps
from datetime import datetime

#recieve origin and destination parameters from sam
origin="Manchester Piccadilly"
destination="Manchester Metropolitan university Business School, uk"

#request directions of all paths and calls algorithm to find lowest crime path. 
#then outputs polyline of lowest crime path 
def get_polyline(origin,destination):
    gmaps = googlemaps.Client(key='AIzaSyDapVav9IuuP5Jjw3ZnDFBqRsFKXN_XIOw')
    now = datetime.now()
    APIresponse = gmaps.directions(origin,destination,
                                     mode="walking",departure_time=now, 
                                     alternatives="true")
    paths=[]

    for routes in APIresponse:
        paths.append(routes["overview_polyline"]['points'])
    
    for i in range(len(paths)):   
        coordinates=decode_polyline(paths[i])[0]
        #latitude=decode_polyline(paths[i])[1]
        #longitude=decode_polyline(paths[i])[2]
        #print(coordinates)
        
        #owen put your algorithm function here...???
        #return lowest_crime (value of i with lowest crime)
        
        #dummy variable
        lowest_crime=0
        
    polyline=paths[lowest_crime]
    return polyline
    
#decode polyline into coordinates 
def decode_polyline(polyline_str):
    '''Pass a Google Maps encoded polyline string; returns list of lat/lon pairs'''
    index, lat, lng = 0, 0, 0
    coordinates = []
    latitude=[]
    longitude=[]
    changes = {'latitude': 0, 'longitude': 0}

    # Coordinates have variable length when encoded, so just keep
    # track of whether we've hit the end of the string. In each
    # while loop iteration, a single coordinate is decoded.
    while index < len(polyline_str):
        # Gather lat/lon changes, store them in a dictionary to apply them later
        for unit in ['latitude', 'longitude']: 
            shift, result = 0, 0

            while True:
                byte = ord(polyline_str[index]) - 63
                index+=1
                result |= (byte & 0x1f) << shift
                shift += 5
                if not byte >= 0x20:
                    break

            if (result & 1):
                changes[unit] = ~(result >> 1)
            else:
                changes[unit] = (result >> 1)

        lat += changes['latitude']
        lng += changes['longitude']

        coordinates.append((lat / 100000.0, lng / 100000.0))
        latitude.append(lat/ 100000.0)
        longitude.append(lng / 100000.0)
        
    return coordinates, latitude, longitude
   
polyline=get_polyline(origin, destination)
print(polyline)
