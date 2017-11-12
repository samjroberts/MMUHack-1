import map_maker_V2 as mm2
import googlemaps
from datetime import datetime
import json
import csv
import datetime as dt
import requests
import numpy as np
from bs4 import BeautifulSoup as bs

from scipy.interpolate import RectBivariateSpline

def index():
    from gluon.tools import geocode
    latA = 53.4774
    longA = -2.2309
    latB = 53.4710
    longB = -2.2390
    locationA = str('Manchester Piccadilly Station')
    locationB = str('Manchester Metropolitan University Business School')
    
    if request.post_vars:
        locationA = str(request.post_vars.locationA)
        locationB = str(request.post_vars.locationB)
        response.flash = T("Coordinates entered!")
    
    polylinefunc = get_polyline(locationA, locationB)
    
    latA = polylinefunc[1][0]
    longA = polylinefunc[1][1]
    latB = polylinefunc[2][0]
    longB = polylinefunc[2][1]
    latMid = (latA + latB)*0.5
    longMid = (longA + longB)*0.5
    
    pathFromPolyline = polylinefunc[3]
    return locals()

# each degree of latitude is 69 miles
def onedeglong(a):
    eq = 69.172
    return(np.cos((np.pi / 180)*a)*eq)

def crime_area(start_lat,start_long,end_lat,end_long,dist):
    start_max_lat1 = start_lat + (dist*1/69)
    start_max_long1 = start_long + (dist*(1/onedeglong(start_lat)))
    end_max_lat1 = end_lat + (dist*1/69)
    end_max_long1 = end_long + (dist*(1/onedeglong(end_lat)))
    start_max_lat2 = start_lat - (dist*1/69)
    start_max_long2 = start_long - (dist*(1/onedeglong(start_lat)))
    end_max_lat2 = end_lat - (dist*1/69)
    end_max_long2 = end_long - (dist*(1/onedeglong(end_lat)))
    
    min_orig_lat = min(start_lat,end_lat)
    min_orig_long = min(start_long,end_long)
    max_orig_lat = max(start_lat,end_lat)
    max_orig_long = max(start_long,end_long)
    
    lat_n = max(start_max_lat1,start_max_lat2,end_max_lat1,end_max_lat2)
    lat_s = min(start_max_lat1,start_max_lat2,end_max_lat1,end_max_lat2)
    long_w = min(start_max_long1,start_max_long2,end_max_long1,end_max_long2)
    long_e = max(start_max_long1,start_max_long2,end_max_long1,end_max_long2)
    
    if start_lat > end_lat:
        long_n = start_long
    else:
        long_n = end_long
        
    if start_lat < end_lat:
        long_s = start_long
    else:
        long_s = end_long
    
    if start_long > end_long:
        lat_e = start_lat
    else:
        lat_e = end_lat
    
    if start_long < end_long:
        lat_w = start_lat
    else:
        lat_w = end_lat
    
    n = [lat_n, long_n]
    s = [lat_s,long_s]
    w = [lat_w,long_w]
    e = [lat_e,long_e]
    
    lat_n = round(n[0],4)
    long_n = round(n[1],4)
    lat_s = round(s[0],4)
    long_s = round(s[1],4)
    lat_w = round(w[0],4)
    long_w = round(w[1],4)
    lat_e = round(e[0],4)
    long_e = round(e[1],4)

    date = dt.date.today()
    
    #possibly add month functionallity
    date = str(date.year)+"-"+str(date.month)
    
    url = "https://data.police.uk/api/crimes-street/all-crime?poly=%s,%s:%s,%s:%s,%s:%s,%s&=%s"     %(str(lat_n),str(long_n),str(lat_s),str(long_s),str(lat_w),str(long_w),str(lat_e),str(long_e),date)

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
def get_risk_map(start_lat, start_long,end_lat,end_long,dist):
    coords = crime_area(start_lat,start_long,end_lat,end_long,dist)
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
    end=decode_polyline(paths[0])[0][-1]
    dist=2
    
    risk_map = get_risk_map(start[0], start[1], end[0], end[1], dist)
    risk_values = []
    
    for path in paths:
        coordinates=decode_polyline(path)[0]
        cart_path = cartesian(coordinates)
        risk_values.append(risk(cart_path, risk_map))
    #minimum risk value
    val, idx = min((val, idx) for (idx, val) in enumerate(risk_values))

    start=(coordinates[0][0],coordinates[0][1])
    end=(coordinates[-1][0],coordinates[-1][1])
    
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
    
    polyline=paths[idx]
    return polyline, start, end, path

#decode polyline into coordinates
def decode_polyline(polyline_str):
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
