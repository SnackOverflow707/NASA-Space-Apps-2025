from flask import Flask, request, jsonify
from utils.dtypes import ValidCoords 
from datetime import datetime 
from flask_cors import CORS

import sys 
import os 
# Get the Backend directory (parent of backend_files)
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.insert(0, backend_dir)
from utils.data_getters import get_openmeteo_weather, get_aqi 

app = Flask(__name__)

CORS(app, resources={
    r"/get_data": {  # ✅ Changed to match new endpoint
        "origins": ["http://localhost:8081"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

BBOX = 0.01  # ✅ Moved to global scope

def set_bbox(latitude, longitude): 
    """Calculate bounding box from coordinates"""
    # ✅ Removed jsonify returns - this is a helper function, not an endpoint
    if latitude is None or longitude is None:
        raise ValueError('Latitude and longitude are required')
        
    # Validate coordinates
    try:
        coords = ValidCoords(float(longitude), float(latitude))
    except Exception as e:
        raise ValueError(f'Invalid coordinates: {str(e)}')

    min_lon = coords.lon - BBOX
    max_lon = coords.lon + BBOX
    min_lat = coords.lat - BBOX
    max_lat = coords.lat + BBOX
    bbox = (min_lon, min_lat, max_lon, max_lat)

    return bbox 

def get_aqi_data(bbox): 
    """Get AQI data for a bounding box"""
    # ✅ Renamed to avoid confusion, removed jsonify
    date = datetime.now().date().strftime("%Y-%m-%d")
    aqi_data = get_aqi(bbox, date)
    return aqi_data  # ✅ Return raw data, not jsonified

def get_weather_data(bbox): 
    """Get weather data for a bounding box"""
    # ✅ Renamed, removed jsonify
    current_weather = get_openmeteo_weather(bbox)
    return current_weather  # ✅ Return raw data, not jsonified

@app.route("/get_data", methods=["POST", "OPTIONS"])  # ✅ Added OPTIONS for CORS
def backend_main(): 
    """Main endpoint that returns both AQI and weather data"""
    # Handle preflight request
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        print("=" * 50)
        print("Received POST request to /get_data")
        
        data = request.get_json()
        print(f"Request data: {data}")
        
        if not data:
            print("ERROR: No data provided")
            return jsonify({'error': 'No data provided'}), 400
        
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        print(f"Latitude: {latitude}, Longitude: {longitude}")
        
        # Get bounding box
        bbox = set_bbox(latitude=latitude, longitude=longitude)
        print(f"Calculated bbox: {bbox}")
        
        # Get data
        print("Fetching AQI data...")
        aqi_data = get_aqi_data(bbox)
        print(f"AQI: {aqi_data}")
        
        print("Fetching weather data...")
        weather_data = get_weather_data(bbox)
        print(f"Weather: {weather_data}")
        
        response = {
            "aqi": aqi_data,
            "current_weather": weather_data
        }
        print(f"Sending response: {response}")
        print("=" * 50)
        
        return jsonify(response), 200  # ✅ Only jsonify at the endpoint level

    except ValueError as e:
        # Handle validation errors
        print(f'Validation error: {str(e)}')
        return jsonify({'error': str(e)}), 400
        
    except Exception as e:
        print("=" * 50)
        print(f'ERROR: Exception occurred - {str(e)}')
        import traceback
        traceback.print_exc()
        print("=" * 50)
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Starting Flask server on port 5001...")
    print("=" * 50)
    app.run(debug=True, port=5001, host='127.0.0.1')