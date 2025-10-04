import xarray as xr
import earthaccess
import pyrsig
import pandas as pd
import os
from datetime import datetime, timedelta
import gzip 
import requests


#Gets pollutant data from NASA's TEMPO and AirNow (US only)
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
    if edate is None:
        edate = bdate
    
    # Generate date list
    start = datetime.strptime(bdate, "%Y-%m-%d")
    end = datetime.strptime(edate, "%Y-%m-%d")
    date_list = []
    current = start
    while current <= end:
        date_list.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    
    # TEMPO pollutants to fetch
    tempo_products = {
        'no2': 'tempo.l2.no2.vertical_column_troposphere',
        'formaldehyde': 'tempo.l2.hcho.vertical_column_troposphere',
        'ozone': 'tempo.l2.o3.vertical_column_troposphere'
    }
    
    # Store data for each pollutant
    all_data = {pollutant: [] for pollutant in tempo_products.keys()}
    airnow_data = {'pm25': [], 'ozone': [], 'no2': []}
    
    # Loop through dates
    for date in date_list:
        print(f"\nFetching data for {date}...")
        
        api = pyrsig.RsigApi(bdate=date, bbox=bbox, workdir=locname, gridfit=True)
        api.tempo_kw["api_key"] = "anonymous"
        
        # Get TEMPO satellite data
        for pollutant, key in tempo_products.items():
            try:
                df = api.to_dataframe(key, unit_keys=False, parse_dates=True, backend="xdr")
                if not df.empty:
                    all_data[pollutant].append(df)
                    print(f"TEMPO {pollutant}: {len(df)} records")
            except Exception as e:
                print(f"Missing TEMPO {pollutant}: {e}")
        
        # Get AirNow ground data
        airnow_products = {
            'pm25': 'airnow.pm25',
            'ozone': 'airnow.ozone',
            'no2': 'airnow.no2'
        }
        
        for pollutant, key in airnow_products.items():
            try:
                df = api.to_dataframe(key, unit_keys=False, parse_dates=True)
                if not df.empty:
                    airnow_data[pollutant].append(df)
                    print(f"AirNow {pollutant}: {len(df)} records")
            except Exception as e:
                print(f"Missing AirNow {pollutant}: Not available")
    
    # Combine data for each pollutant
    combined_data = {}
    
    for pollutant in tempo_products.keys():
        if all_data[pollutant]:
            combined_data[f'tempo_{pollutant}'] = pd.concat(all_data[pollutant], ignore_index=True)
            combined_data[f'tempo_{pollutant}'] = combined_data[f'tempo_{pollutant}'].sort_values('time')
    
    for pollutant in airnow_products.keys():
        if airnow_data[pollutant]:
            combined_data[f'airnow_{pollutant}'] = pd.concat(airnow_data[pollutant], ignore_index=True)
            combined_data[f'airnow_{pollutant}'] = combined_data[f'airnow_{pollutant}'].sort_values('time')
    
    # Summary
    print(f"\n{'='*60}")
    print("Data Summary:")
    for key, df in combined_data.items():
        print(f"  {key}: {len(df)} records")
    print(f"{'='*60}\n")
    
    return combined_data



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

