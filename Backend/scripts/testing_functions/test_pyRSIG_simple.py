import xarray as xr
import earthaccess
import pyrsig
import pandas as pd
import os
from datetime import datetime, timedelta
import requests
import numpy as np 
import shutil 

#goal: test TEMPO data uploads. 
lat = 49.2
lon = -122.2

class ValidCoords:
    
    MIN_LON = -130  # west
    MAX_LON = -60   # east
    MIN_LAT = 15    # south
    MAX_LAT = 60    # north

    def __init__(self, longitude, latitude):

        if not isinstance(longitude, (int, float)):
            raise TypeError("Longitude must be a number (int or float)")
        if not isinstance(latitude, (int, float)): 
            raise TypeError("Latitude must be a number (int or float)")

        self.validate_coords(longitude, latitude)
        
        self.lon = longitude
        self.lat = latitude

    def validate_coords(self, longitude, latitude): 

        if longitude < self.MIN_LON:
            raise ValueError(f"Longitude must be >= {self.MIN_LON} deg.")
        if longitude > self.MAX_LON:
            raise ValueError(f"Longitude must be <= {self.MAX_LON} deg.")
        if latitude < self.MIN_LAT:
            raise ValueError(f"Latitude must be >= {self.MIN_LAT} deg.")
        if latitude > self.MAX_LAT:
            raise ValueError(f"Latitude must be <= {self.MAX_LAT} deg.")
        
    def print_coords(self): 
        print(f"Latitude: {self.lat}; longitude: {self.lon}\n")

in_coords = ValidCoords(latitude=lat, longitude=lon)

BBOX = 0.5

min_lon = in_coords.lon - BBOX
max_lon = in_coords.lon + BBOX
min_lat = in_coords.lat - BBOX
max_lat = in_coords.lat + BBOX

bbox = (min_lon, min_lat, max_lon, max_lat)

bdate="2025-07-05T00"
edate= datetime.now().isoformat(timespec='seconds')
print("Begin date", bdate)
print("End date", edate)

rsigapi = pyrsig.RsigApi(bdate=bdate, edate=edate, bbox=bbox, workdir="pyrsig_cache")
tkey = 'none'
rsigapi.tempo_kw['api_key'] = tkey

descdf = rsigapi.descriptions()
print(descdf[:10])
print(type(descdf))
query = descdf.query('name.str.contains("tempo")')
print("Query columns: ", query.columns)
query2 = descdf.query('name.str.contains("no2.vertical_column")')
print(query2)
query3 = descdf.query('name.str.contains("hcho.vertical_column")')
print(query3)

print("Tempo data for NO2: ", descdf[descdf["name"] == "tempo.l2.no2.vertical_column_troposphere"])
print("pm data: ", descdf.query('name.str.contains("pm25")')) 


tempodf = rsigapi.to_dataframe(
    'tempo.l2.no2.vertical_column_troposphere',
    unit_keys=False, parse_dates=True, verbose=9
)
print("tempodf: ", tempodf[:-10])






"""
# Create spatial medians for TEMPO and AirNow
tempods = tempodf.groupby(pd.Grouper(key='time', freq='1h')).median(numeric_only=True)[
    'no2_vertical_column_troposphere'
]
# Get AirNow NO2 with dates parsed and units removed from column names
andf = rsigapi.to_dataframe(
    'airnow.no2', parse_dates=True, unit_keys=False, verbose=9
)
ands = andf.groupby(['time']).median(numeric_only=True)['no2']
"""