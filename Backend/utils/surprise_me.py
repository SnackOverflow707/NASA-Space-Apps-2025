import pandas as pd
from datetime import datetime
import numpy as np 
import random 
from utils.dtypes import ValidCoords
from utils.data_getters import get_openmeteo_weather, set_bbox


north_american_cities = {
    "New York, USA": {"lat": 40.7128, "lon": -74.0060},
    "Los Angeles, USA": {"lat": 34.0522, "lon": -118.2437},
    "Chicago, USA": {"lat": 41.8781, "lon": -87.6298},
    "Houston, USA": {"lat": 29.7604, "lon": -95.3698},
    "Phoenix, USA": {"lat": 33.4484, "lon": -112.0740},
    "Philadelphia, USA": {"lat": 39.9526, "lon": -75.1652},
    "San Antonio, USA": {"lat": 29.4241, "lon": -98.4936},
    "San Diego, USA": {"lat": 32.7157, "lon": -117.1611},
    "Dallas, USA": {"lat": 32.7767, "lon": -96.7970},
    "San Jose, USA": {"lat": 37.3382, "lon": -121.8863},
    "Toronto, Canada": {"lat": 43.6532, "lon": -79.3832},
    "Montreal, Canada": {"lat": 45.5017, "lon": -73.5673},
    "Vancouver, Canada": {"lat": 49.2827, "lon": -123.1207},
    "Ottawa, Canada": {"lat": 45.4215, "lon": -75.6972},
    "Mexico City, Mexico": {"lat": 19.4326, "lon": -99.1332},
    "Guadalajara, Mexico": {"lat": 20.6597, "lon": -103.3496},
    "Monterrey, Mexico": {"lat": 25.6866, "lon": -100.3161},
    "Tijuana, Mexico": {"lat": 32.5149, "lon": -117.0382},
    "Cancun, Mexico": {"lat": 21.1619, "lon": -86.8515},
    "Miami, USA": {"lat": 25.7617, "lon": -80.1918},
    "Atlanta, USA": {"lat": 33.7490, "lon": -84.3880},
    "Seattle, USA": {"lat": 47.6062, "lon": -122.3321},
    "Boston, USA": {"lat": 42.3601, "lon": -71.0589},
    "Denver, USA": {"lat": 39.7392, "lon": -104.9903},
    "Minneapolis, USA": {"lat": 44.9778, "lon": -93.2650},
    "Quebec City, Canada": {"lat": 46.8139, "lon": -71.2080},
    "Calgary, Canada": {"lat": 51.0447, "lon": -114.0719},
    "Winnipeg, Canada": {"lat": 49.8951, "lon": -97.1384}, 
    "Edmonton, Canada": {"lat": 53.55, "lon": -113.49},
    "Havana, Cuba": {"lat": 23.13, "lon": -82.36},
    "Santo Domingo, Dominican Republic": {"lat": 18.46, "lon": -69.94},
    "Panama City, Panama": {"lat": 8.98, "lon": -79.52},
    "San Juan, Puerto Rico": {"lat": 18.42, "lon": -66.06}
}


def surprise_me(): 

    MIN_LON = -130  # west
    MAX_LON = -60   # east
    MIN_LAT = 15    # south
    MAX_LAT = 60    # north

    names = list(north_american_cities.keys())
    city_lat = 0 
    city_lon = 0

    while (city_lat < MIN_LAT or city_lat > MAX_LAT or city_lon < MIN_LON or city_lon > MAX_LON): 

        city = random.choice(names)
        city_lat = north_american_cities[city]['lat']
        city_lon = north_american_cities[city]['lon']
    
    newCoords = ValidCoords(longitude=city_lon, latitude=city_lat)

    bbox = set_bbox(newCoords.lat, newCoords.lon)
    return get_openmeteo_weather(bbox)['current']









