import pyrsig
import pandas as pd

import sys
import os
# Add Backend folder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from utils.functions import get_no2_data
from utils.dtypes import ValidCoords

BBOX = 0.1

#lat = float(input("Enter latitude: "))
#lon = float(input("Enter longitude: "))

lat = 49.2
lon = -122.2

in_coords = ValidCoords(latitude=lat, longitude=lon)

min_lon = in_coords.lon - BBOX
max_lon = in_coords.lon + BBOX
min_lat = in_coords.lat - BBOX
max_lat = in_coords.lat + BBOX

bbox = (min_lon, min_lat, max_lon, max_lat)
date="2025-10-02"

no2_dict = get_no2_data(bbox=bbox, bdate=date)
for key in no2_dict.keys(): 
    print("Key: ", key) 





# Save to CSV (optional)
#tempo_hourly.to_csv(os.path.join(output_dir, "tempo_no2_hourly.csv"))
#airnow_hourly.to_csv(os.path.join(output_dir, "airnow_no2_hourly.csv"))
 