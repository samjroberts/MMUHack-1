# coding: utf-8

# In[1]:

import json
import csv
import datetime as dt
import requests
from bs4 import BeautifulSoup as bs
import numpy as np

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