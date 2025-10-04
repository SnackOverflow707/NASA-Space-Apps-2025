import earthaccess

import sys
import os
# Add Backend folder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from utils.dtypes import ValidCoords 
from datetime import datetime

BBOX = 0.1
GRANULE_COUNT = 5

lon = float(input("Enter longitude: "))
lat = float(input("Enter latitude: ")) 

in_coords = ValidCoords(latitude=lat, longitude=lon)
in_coords.print_coords() 

min_lon = in_coords.lon - BBOX
max_lon = in_coords.lon + BBOX
min_lat = in_coords.lat - BBOX
max_lat = in_coords.lat + BBOX

bbox = (min_lon, min_lat, max_lon, max_lat)

while True:
    try:
        min_date = datetime.strptime(input("Enter start date (yyyy-mm-dd): "), "%Y-%m-%d")
        max_date = datetime.strptime(input("Enter end date (yyyy-mm-dd): "), "%Y-%m-%d")
        if max_date <= min_date:
            raise ValueError("End date must be after start date.")
        break
    except ValueError as e:
        print(f"Invalid input: {e}. Please try again.")

results = earthaccess.search_data(
    short_name="TEMPO_NO2_L2", 
    version="V04",  
    bounding_box=bbox,  
    temporal=(min_date, max_date), #Dates can be datetime objects or ISO 8601 formatted strings. 
    count=GRANULE_COUNT
)

print(results)

