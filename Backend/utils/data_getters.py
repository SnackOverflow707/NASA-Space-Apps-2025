import xarray as xr
import earthaccess
import pyrsig
import pandas as pd
import os
from datetime import datetime, timedelta
import gzip 
import requests

#Get no2 data from NASA's TEMPO 
def get_pollutants(bbox, bdate, edate=None, tempokey="tempo.l2.no2.vertical_column_troposphere", locname="pyrsig_cache"):
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
    pollutants = {
        'no2': 'tempo.l2.no2.vertical_column_troposphere',
        'formaldehyde': 'tempo.l2.hcho.vertical_column_troposphere',
        'ozone': 'tempo.l2.o3.vertical_column_troposphere'
    }
    if tempokey not in pollutants.items(): 
        raise ValueError("Unknown pollutant or metric passed into function.")

    # If no end date, just use start date
    if edate is None:
        edate = bdate
    
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



#Get weather data from NASA's merra2 (LAG: Data is only available 2-3 weeks after)
def get_merra2_weather(bbox, date):
    """
    Get MERRA-2 reanalysis weather data from NASA
    Includes boundary layer height!
    
    Parameters:
    -----------
    bbox : tuple
        (min_lon, min_lat, max_lon, max_lat)
    date : str
        Date in "YYYY-MM-DD" format
    """
    # Authenticate
    earthaccess.login()
    
    # Search for MERRA-2 data
    # M2T1NXSLV: Single-Level Diagnostics (temp, wind, pressure, etc.)
    results = earthaccess.search_data(
        short_name='M2T1NXSLV',
        temporal=(date, date),
        bounding_box=bbox
    )
    
    print(f"Found {len(results)} granules")
    
    if len(results) == 0:
        print("No data found.")
        return None
    
    # Open files with explicit engine
    print("Opening files...")
    try:
        files = earthaccess.open(results)
        # Try netcdf4 engine explicitly
        try:
            ds = xr.open_mfdataset(files, engine='netcdf4', combine='by_coords')
            #print("✓ Opened with netcdf4 engine")
        except:
            # Fallback to h5netcdf
            ds = xr.open_mfdataset(files, engine='h5netcdf', combine='by_coords')
            #print("✓ Opened with h5netcdf engine")
        
        # Subset to bounding box
        ds_subset = ds.sel(
            lon=slice(bbox[0], bbox[2]),
            lat=slice(bbox[1], bbox[3])
        )
        
        # Extract variables
        weather_data = {
            'time': ds_subset['time'].values,
            'lat': ds_subset['lat'].values,
            'lon': ds_subset['lon'].values,
            'temp_2m': ds_subset['T2M'].values,
            'wind_u_10m': ds_subset['U10M'].values,
            'wind_v_10m': ds_subset['V10M'].values,
            'humidity': ds_subset['QV2M'].values,
            'pressure': ds_subset['PS'].values,
            'precip_total': ds_subset['PRECTOT'].values,
            'pbl_height': ds_subset['PBLH'].values
        }
        
        print(f"Successfully loaded MERRA-2 data")     
        return weather_data
    
    except Exception as e:
        print(f"Error opening files: {e}")
        return None


def get_openmeteo_weather(bbox, forecast_hours=48):
    """
    Get weather data from Open-Meteo (FREE, no API key!)
    Includes current conditions + forecast
    
    Parameters:
    -----------
    lat, lon : float
        Location coordinates
    forecast_hours : int
        Hours of forecast (up to 384 hours = 16 days)
    
    Returns:
    --------
    dict with current and forecast weather data. Units: 
    Temperature - celsius 
    relative humidity - %
    surface_pressure - hPa 
    wind_speed_10m - km/h
    wind_direction_10m - 0-360 degrees (0=North, 90=East, 180=South, 270=West)
    precipitation - mm 
    cloud_cover - % 
    """
    # API endpoint
    url = "https://api.open-meteo.com/v1/forecast"

    center_lat = (bbox[1] + bbox[3]) / 2
    center_lon = (bbox[0] + bbox[2]) / 2
    
    # Parameters - request ALL the variables you need
    params = {
        'latitude': center_lat,
        'longitude': center_lon,
        'hourly': [
            'temperature_2m',
            'relative_humidity_2m',
            'dew_point_2m',
            'precipitation',
            'surface_pressure',
            'cloud_cover',
            'wind_speed_10m',
            'wind_direction_10m',
            'wind_gusts_10m',
        ],
        'current': [
            'temperature_2m',
            'relative_humidity_2m',
            'precipitation',
            'surface_pressure',
            'cloud_cover',
            'wind_speed_10m',
            'wind_direction_10m'
        ],
        'temperature_unit': 'celsius',
        'wind_speed_unit': 'ms',
        'precipitation_unit': 'mm',
        'timezone': 'auto',
        'forecast_days': min(16, (forecast_hours // 24) + 1)
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    # Parse current weather
    current = {
        'time': datetime.fromisoformat(data['current']['time']),
        'temp': data['current']['temperature_2m'],
        'humidity': data['current']['relative_humidity_2m'],
        'pressure': data['current']['surface_pressure'],
        'wind_speed': data['current']['wind_speed_10m'],
        'wind_direction': data['current']['wind_direction_10m'],
        'precipitation': data['current']['precipitation'],
        'cloud_cover': data['current']['cloud_cover']
    }
    
    # Parse hourly forecast
    hourly = data['hourly']
    forecast = []
    
    for i in range(min(forecast_hours, len(hourly['time']))):
        forecast.append({
            'time': datetime.fromisoformat(hourly['time'][i]), 
            'temp': hourly['temperature_2m'][i],
            'humidity': hourly['relative_humidity_2m'][i],
            'pressure': hourly['surface_pressure'][i],
            'wind_speed': hourly['wind_speed_10m'][i],
            'wind_direction': hourly['wind_direction_10m'][i],
            'precipitation': hourly['precipitation'][i],
            'cloud_cover': hourly['cloud_cover'][i]
        })
    
    return {
        'current': current,
        'forecast': forecast
    }

