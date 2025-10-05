from flask import Flask, request, jsonify
from utils.dtypes import ValidCoords 
from datetime import datetime 
from flask_cors import CORS

import sys 
import os 
# Get the Backend directory (parent of backend_files)
current_dir = os.path.dirname(os.path.abspath(__file__))  # Backend/backend_files/
backend_dir = os.path.dirname(current_dir)  # Backend/
sys.path.insert(0, backend_dir)  # Add Backend/ to path
from utils.data_getters import get_openmeteo_weather, rate_aqi, get_aqi 

app = Flask(__name__)

CORS(app, resources={
    r"/aqi": {
        "origins": ["http://localhost:8081"],  # Your frontend URL
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

BBOX = 0.1

@app.route('/aqi', methods=['POST', 'OPTIONS'])
def get_aqi_endpoint():
    # Handle preflight request
    if request.method == 'OPTIONS':
        print("Received OPTIONS request (CORS preflight)")
        return '', 200
        
    try:
        print("=" * 50)
        print("Received POST request to /aqi")
        
        # Get JSON data from request
        data = request.get_json()
        print(f"Request data: {data}")
        
        if not data:
            print("ERROR: No data provided")
            return jsonify({'error': 'No data provided'}), 400
        
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        print(f"Extracted - Latitude: {latitude}, Longitude: {longitude}")
        
        if latitude is None or longitude is None:
            print("ERROR: Missing latitude or longitude")
            return jsonify({'error': 'Latitude and longitude are required'}), 400
        
        # Validate coordinates
        try:
            coords = ValidCoords(float(longitude), float(latitude))
            print(f"Validated coords: lat={coords.lat}, lon={coords.lon}")
        except Exception as e:
            print(f"ERROR: Validation failed - {str(e)}")
            return jsonify({'error': f'Invalid coordinates: {str(e)}'}), 400
        
        min_lon = coords.lon - BBOX
        max_lon = coords.lon + BBOX
        min_lat = coords.lat - BBOX
        max_lat = coords.lat + BBOX
        bbox = (min_lon, min_lat, max_lon, max_lat)
        print(f"Calculated bbox: {bbox}")
        
        #get date 
        date = datetime.now().date().strftime("%Y-%m-%d")
        print(f"Using date: {date}")
        
        # Get AQI data using your existing function
        print("Calling get_aqi()...")
        aqi_data = get_aqi(bbox, date)
        print(f"AQI data received: {aqi_data}")
        
        response_data = {'aqi': aqi_data}
        print(f"Sending response: {response_data}")
        print("=" * 50)
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print("=" * 50)
        print(f'ERROR: Exception occurred - {str(e)}')
        import traceback
        traceback.print_exc()
        print("=" * 50)
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
    
@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Server is running!'}), 200

    
if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Starting Flask server on port 5001...")
    print("=" * 50)
    app.run(debug=True, port=5001, host='127.0.0.1')