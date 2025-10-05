import xarray as xr
import earthaccess
import pyrsig
import pandas as pd
import os
from datetime import datetime, timedelta
import gzip 
import requests
import numpy as np 
import shutil 


#Gets pollutant data from NASA's TEMPO and AirNow (US only)
def get_pollutants(bbox, bdate, edate=None, prevyrs=None, locname="pyrsig_cache"):
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
    prevyrs : int, optional
        Number of previous years to fetch data for the same date(s).
        For example, if bdate="2025-10-02" and prevyrs=3, will fetch
        data for 2025-10-02, 2024-10-02, 2023-10-02, and 2022-10-02.
    locname : str, optional
        Location name for working directory. If None, uses date range as name.
        
    Returns:
    --------
    dict : Dictionary containing pollutant data with year labels
    """  
    if edate is None:
        edate = bdate
    
    # Generate base date list
    start = datetime.strptime(bdate, "%Y-%m-%d")
    end = datetime.strptime(edate, "%Y-%m-%d")
    base_dates = []
    current = start
    while current <= end:
        base_dates.append(current)
        current += timedelta(days=1)
    
    # If prevyrs is specified, create dates for previous years
    all_dates = []
    if prevyrs:
        for year_offset in range(prevyrs, -1, -1):  # Goes from prevyrs down to 0
            for date in base_dates:
                # Subtract years from the date
                prev_date = date.replace(year=date.year - year_offset)
                all_dates.append(prev_date)
    else:
        all_dates = base_dates
    
    # Convert to string format
    date_list = [d.strftime("%Y-%m-%d") for d in all_dates]
    print("Date list: ", date_list)
    
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
        cache_dir = "pyrsig_cache"
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)

        api = pyrsig.RsigApi(bdate=date, bbox=bbox, workdir=locname, gridfit=True)
        api.tempo_kw["api_key"] = "anonymous"
        
        # Get TEMPO satellite data
        for pollutant, key in tempo_products.items():
            try:
                df = api.to_dataframe(key, unit_keys=False, parse_dates=True, backend="xdr")
                if not df.empty:
                    # Add year column to track which year this data is from
                    df['year'] = datetime.strptime(date, "%Y-%m-%d").year
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
                    # Add year column
                    df['year'] = datetime.strptime(date, "%Y-%m-%d").year
                    airnow_data[pollutant].append(df)
                    print(f"AirNow {pollutant}: {len(df)} records")
            except Exception as e:
                print(f"Missing AirNow {pollutant}: Not available")
    
    # Combine data for each pollutant
    combined_data = {}
    
    for pollutant in tempo_products.keys():
        if all_data[pollutant]:
            combined_data[f'tempo_{pollutant}'] = pd.concat(all_data[pollutant], ignore_index=True)
            combined_data[f'tempo_{pollutant}'] = combined_data[f'tempo_{pollutant}'].sort_values(['year', 'time'])
    
    for pollutant in airnow_products.keys():
        if airnow_data[pollutant]:
            combined_data[f'airnow_{pollutant}'] = pd.concat(airnow_data[pollutant], ignore_index=True)
            combined_data[f'airnow_{pollutant}'] = combined_data[f'airnow_{pollutant}'].sort_values(['year', 'time'])
    
    # Summary
    print(f"\n{'='*60}")
    print("Data Summary:")
    for key, df in combined_data.items():
        print(f"  {key}: {len(df)} records")
        if prevyrs:
            years = df['year'].unique()
            print(f"    Years included: {sorted(years)}")
    print(f"{'='*60}\n")
    
    return combined_data


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


def get_aqi(bbox, start_date, end_date=None, hour=None): 

    # API endpoint
    center_lat = (bbox[1] + bbox[3]) / 2
    center_lon = (bbox[0] + bbox[2]) / 2
  
    current_date = datetime.now().date() # gets according to the local time

    if end_date is None:
        end_date = start_date  
    
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    if hour == None: 
        if start_date == current_date: 
            hour = datetime.now().hour  

    # Convert back to standardized YYYY-MM-DD strings
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")

    #url = "https://api.open-meteo.com/v1/air-quality" 
    params = {
        'latitude': center_lat, 
        'longitude': center_lon, 
        'hourly': 'us_aqi', 
        'start_date': start_date, 
        'end_date': end_date 
    }

    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={center_lat}&longitude={center_lon}&start_date={start_date}&end_date={end_date}&hourly=us_aqi"
    response = requests.get(url, params)

    data = response.json()
    us_aqi = data[0]['hourly']['us_aqi']

    if hour is not None: 
        return int(us_aqi[hour]) #current aqi 
    
    else: 
        accum = 0
        for rating in us_aqi: 
            accum += rating 

        return int(accum / len(us_aqi)) #average aqi over specified range 


def rate_aqi(aqi): 

    if aqi < 0:
        raise ValueError("Invalid negative value for AQI.")

    # Define ranges
    VERY_GOOD = np.arange(0, 34)
    GOOD = np.arange(34, 67)
    FAIR = np.arange(67, 100)
    POOR = np.arange(100, 150)
    VERY_POOR = np.arange(150, 201)
    
    # Map ranges to strings
    rating_list = [
        (VERY_GOOD, "verygood"),
        (GOOD, "good"),
        (FAIR, "fair"),
        (POOR, "poor"),
        (VERY_POOR, "verypoor")
    ]

    # Check which range AQI falls in
    for rng, label in rating_list:
        if aqi in rng:
            return label
    
    # If AQI is outside all ranges
    return "hazardous" 







    








