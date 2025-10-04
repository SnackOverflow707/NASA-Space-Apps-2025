import xarray as xr
import earthaccess
import pyrsig
import pandas as pd
import os
from datetime import datetime, timedelta
import gzip 

def login():
    auth = earthaccess.login(strategy="netrc")
    return auth

"""This requires users to create an netrc file with ~/.netrc and adding the following: 
machine urs.earthdata.nasa.gov
login YOUR_USERNAME
password YOUR_PASSWORD

I've found this is better than setting an environment variable, because I can't get that version to work. 
"""

def get_data(auth):
    session = auth.get_fsspec_session()
    # Example: download a file
    # session.get("https://example.earthdata.nasa.gov/file.nc", "file.nc")
    return "data downloaded"

def get_opendap_url(granule):
    related_urls = granule['umm']['RelatedUrls']
    print(related_urls)
    for url_info in related_urls:
        if url_info.get("Subtype") == "OPENDAP DATA":
            return url_info["URL"]
    return None  # if no OPeNDAP found



def get_no2(dataset: str): 

    if dataset[-3:] != ".nc":
        raise ValueError(f".nc file expected. Instead got filetype: {dataset[dataset.find(".") + 1:]}\n")
    # Load the file
    #ds = xr.open_dataset(dataset)
    ds = xr.open_dataset(dataset, engine="netcdf4")

    # Access the tropospheric NO2 column
    no2 = ds['NO2_VERTICAL_CO']
    print(no2[:10])



def get_no2_data(bbox, bdate, edate=None, tempokey="tempo.l2.no2.vertical_column_troposphere", locname=None):
    """
    Fetch and process TEMPO and AirNow air quality data for a date range.
    
    Parameters:
    -----------
    bbox : tuple
        Bounding box as (min_lon, min_lat, max_lon, max_lat)
    bdate : str
        Start date in format "YYYY-MM-DD"
    edate : str, optional
        End date in format "YYYY-MM-DD". If None, only fetches bdate.
    tempokey : str, optional
        TEMPO data key (default: NO2 vertical column troposphere)
    locname : str, optional
        Location name for working directory. If None, uses date range as name.
        
    Returns:
    --------
    dict : Dictionary containing:
        - 'tempo_hourly': Hourly averaged TEMPO data (all columns)
        - 'tempo_no2_hourly': Hourly averaged TEMPO NO2 only
        - 'airnow_no2_hourly': Hourly median AirNow NO2 (or empty if no data)
        - 'tempo_df': Raw TEMPO dataframe
        - 'airnow_df': Raw AirNow dataframe (or empty if no data)
        - 'date_range': List of dates processed
        - 'airnow_available': Boolean indicating if AirNow data was found
    """
    # If no end date, just use start date
    if edate is None:
        edate = bdate
    
    # Use date range as locname if not provided
    if locname is None:
        if bdate == edate:
            locname = bdate.replace("-", "")
        else:
            locname = f"{bdate.replace('-', '')}_to_{edate.replace('-', '')}"
    
    # Generate list of dates
    start = datetime.strptime(bdate, "%Y-%m-%d")
    end = datetime.strptime(edate, "%Y-%m-%d")
    date_list = []
    current = start
    while current <= end:
        date_list.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    
    # Initialize lists to store data from each day
    tempo_dfs = []
    airnow_dfs = []
    airnow_available = False
    
    # Loop through each date
    for date in date_list:
        print(f"Fetching data for {date}...")
        
        try:
            # Initialize API for this date
            api = pyrsig.RsigApi(bdate=date, bbox=bbox, workdir=locname, gridfit=True)
            api_key = "anonymous"
            api.tempo_kw["api_key"] = api_key
            
            # Fetch TEMPO data
            try:
                tempo_df = api.to_dataframe(tempokey, unit_keys=False, parse_dates=True, backend="xdr")
                if not tempo_df.empty:
                    tempo_dfs.append(tempo_df)
                    print(f"TEMPO data: {len(tempo_df)} records")
                else:
                    print(f"TEMPO data: No records found")
            except Exception as e:
                print(f"TEMPO data failed: {e}")
            
            # Fetch AirNow data with error handling
            try:
                airnowkey = "airnow.no2"
                airnow_df = api.to_dataframe(airnowkey, unit_keys=False, parse_dates=True)
                if not airnow_df.empty:
                    airnow_dfs.append(airnow_df)
                    airnow_available = True
                    print(f"AirNow data: {len(airnow_df)} records")
                else:
                    print(f"AirNow data: No records found")
            except (gzip.BadGzipFile, pd.errors.EmptyDataError, FileNotFoundError) as e:
                print(f"AirNow data not available (no monitoring stations in area or corrupted data)")
            except Exception as e:
                print(f"AirNow data failed: {e}")
            
        except Exception as e:
            print(f"API error for {date}: {e}")
            continue
    
    # Combine all dataframes
    tempo_df_combined = pd.concat(tempo_dfs, ignore_index=True) if tempo_dfs else pd.DataFrame()
    airnow_df_combined = pd.concat(airnow_dfs, ignore_index=True) if airnow_dfs else pd.DataFrame()
    
    # Sort by time
    if not tempo_df_combined.empty:
        tempo_df_combined = tempo_df_combined.sort_values('time')
    if not airnow_df_combined.empty:
        airnow_df_combined = airnow_df_combined.sort_values('time')
    
    # Calculate hourly averages on combined data
    tempo_hourly = pd.DataFrame()
    tempo_no2_hourly = pd.Series(dtype=float)
    airnow_no2_hourly = pd.Series(dtype=float)
    
    if not tempo_df_combined.empty:
        tempo_hourly = tempo_df_combined.groupby(pd.Grouper(key="time", freq="1h")).mean(numeric_only=True)
        tempo_no2_hourly = tempo_df_combined.groupby(pd.Grouper(key="time", freq="1h"))["no2_vertical_column_troposphere"].mean()
    
    if not airnow_df_combined.empty:
        airnow_no2_hourly = airnow_df_combined.groupby(pd.Grouper(key="time", freq="1h"))["no2"].median()
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  Dates processed: {len(date_list)}")
    print(f"  TEMPO records: {len(tempo_df_combined)}")
    print(f"  AirNow records: {len(airnow_df_combined)}")
    print(f"  AirNow available: {airnow_available}")
    print(f"{'='*50}\n")
    
    return {
        'tempo_hourly': tempo_hourly,
        'tempo_no2_hourly': tempo_no2_hourly,
        'airnow_no2_hourly': airnow_no2_hourly,
        'tempo_df': tempo_df_combined,
        'airnow_df': airnow_df_combined,
        'date_range': date_list,
        'airnow_available': airnow_available
    }

