import googlemaps
from datetime import datetime
import json
import csv
import datetime as dt
import requests
#from bs4 import BeautifulSoup as bs
import numpy as np
#import matplotlib.pyplot as plt
from scipy.interpolate import RectBivariateSpline

#recieve origin and destination parameters from sam
origin="M16 0DA"
destination="M17 1PG"

#get data around origin point
def crime_coords(x,y):
    date = dt.date.today()
    date = str(date.year)+"-"+str(date.month-2)
    
    inp_n = x
    inp_e = y
    
    url = "https://data.police.uk/api/crimes-street/all-crime?lat=%s&lng=%s&date=%s" \
    %(str(inp_n),str(inp_e),date)
    
    url_json = requests.get(url).json()
    
    lats = []
    longs = []
    
    for i in range(len(url_json)):
        lats.append(url_json[i]['location']['latitude'])
        longs.append(url_json[i]['location']['longitude'])
    points = np.column_stack((lats,longs))
    points = [[float(p[0]), float(p[1])] for p in points ]
    #converts to cartesian
    return cartesian(points)

#get risk map around start point of path
def get_risk_map(lat0,long0):
    coords = crime_coords(lat0, long0)
    risk_map = interpolate(coords)
    return risk_map

#interpolate crime incidence map
def interpolate(coords):
    x = [p[0] for p in coords]
    y = [p[1] for p in coords]
    H, xedges, yedges = np.histogram2d(x, y, bins=[10, 10])
    delta = xedges[1] - xedges[0]
    xmid = np.array([0.5*(xedges[i+1]+xedges[i]) for i in range(len(xedges)-1)])
    ymid= np.array([0.5*(yedges[i+1]+yedges[i]) for i in range(len(yedges)-1)])
    f = RectBivariateSpline(xmid, ymid, H)
    return f

#(latitude, longitude)->(cartesian)
def scale_factor(lat):
    eq = 69.172
    return [1, np.cos((np.pi/180)*lat)*eq]
    #s_lat = 111132.92-559.82*np.cos(2*u) + 1.175*np.cos(4*u) - 0.0023*np.cos(6*u)
    #s_long = 111412.84*np.cos(u) - 93.5*np.cos(3*u) + 0.118*np.cos(5*u)

#turns path of (lat, long) values to cartesian
def cartesian(path):
    lat0 = path[0][0]
    long0 = path[0][1]
    s_lat, s_long = scale_factor(lat0)
    path = [[s_lat*(u-lat0), s_long*(v-long0)] for [u, v] in path]
    return path

#finds risk associated with path
def risk(path, risk_map):
    I = 0
    for i in range(len(path)-1):
        p1 = path[i+1]
        p0 = path[i]
        x = (p1[1]+p0[0])*0.5
        y = (p1[1]+p0[0])*0.5
        dS = np.sqrt((p1[1]-p0[1])**2 + (p1[0]-p0[0])**2)
        I += risk_map(x, y)*dS
    return I

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
    start=decode_polyline(paths[0])[0][1]
    risk_map = get_risk_map(start[0], start[1])
    risk_values = []
    for path in paths:
        coordinates=decode_polyline(path)[0]
        cart_path = cartesian(coordinates)
        risk_values.append(risk(cart_path, risk_map))
    #minimum risk value
    val, idx = min((val, idx) for (idx, val) in enumerate(risk_values))
    polyline=paths[idx]
    
    path = []
    latitudes = decode_polyline(paths[idx])[1]
    longitudes = decode_polyline(paths[idx])[2]
    
    i = 0;
    for x in latitudes:
        coord_array=[]
        coord_array.append(latitudes[i])
        coord_array.append(longitudes[i])
        path.append(coord_array)
        i+=1
    
    
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