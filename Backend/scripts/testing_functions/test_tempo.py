#from utils.data_getters import get_pollutants_tempo
#from utils.dtypes import ValidCoords
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd 
import pyrsig 
import os
import shutil 


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
        
in_coords = ValidCoords(latitude=lat, longitude=lon)

BBOX = 0.1

min_lon = in_coords.lon - BBOX
max_lon = in_coords.lon + BBOX
min_lat = in_coords.lat - BBOX
max_lat = in_coords.lat + BBOX

bbox = (min_lon, min_lat, max_lon, max_lat)

def get_pollutants(bbox, bdate=None, locname="pyrsig_cache", months=1): 

    pollutants = {
        'no2': 'tempo.l2.no2.vertical_column_troposphere',
        #'formaldehyde': 'tempo.l2.hcho.vertical_column_troposphere',
        'hcho': 'tempo.l3.hcho.vertical_column', 
        'o3': 'tempo.l2.o3tot.column_amount_o3', 
        'pm25': 'airnow.pm25'
    }
    pollutants_data = {
        "no2": [], 
        "hcho": [], 
        "o3": [], 
        "pm25": []
    }

    if bdate==None: 
        bdate = datetime.now() - relativedelta(months=months)
    
    edate=datetime.now().isoformat(timespec='seconds')
    rsigapi = pyrsig.RsigApi(bdate=bdate, edate=edate, bbox=bbox, workdir="pyrsig_cache")
    tkey = 'none'
    rsigapi.tempo_kw['api_key'] = tkey

    for key, value in pollutants.items(): 
        try: 
            print(f"adding data from {bdate} to {edate} for {key}.\n")
            tempodf = rsigapi.to_dataframe(
                value,
                unit_keys=False, parse_dates=True, verbose=9
            )
            print(f"{key} Dataframe: ", tempodf[:-10])
            print("Dataframe length: ", len(tempodf))
            cols = tempodf.filter(like=f"key").columns

            data_col = cols[0]
            print("grabbing data from column ", data_col)
            pollutants_data[key].append(tempodf[data_col])

            
        except Exception as e:
            print(f"Error processing {key}: {e}")
            
            # Check if it's a gzip error (corrupted download)
            if "gzip" in str(e).lower() or "not a gzipped file" in str(e).lower():
                print(f"Corrupted file detected for {key}, clearing cache...")
                
                # Remove the entire cache directory and recreate it
                if os.path.exists(locname) and os.path.isdir(locname):
                    try:
                        shutil.rmtree(locname)  # Remove directory and all contents
                        os.makedirs(locname)  # Recreate empty directory
                        print(f"Cleared cache directory: {locname}")
                    except Exception as cleanup_error:
                        print(f"Failed to clear cache: {cleanup_error}")
                
                pollutants_data[key].append(None)
            else:
                print(f"Non-gzip error for {key}, skipping...")
                pollutants_data[key].append(None)
    
    return pollutants_data
            


res = get_pollutants(bbox)