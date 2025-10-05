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
from utils.data_getters import get_openmeteo_weather, get_aqi 

app = Flask(__name__)

CORS(app, resources={
    r"/aqi": {
        "origins": ["http://localhost:8081"],  # Your frontend URL
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

BBOX = 0.01

@app.route('/aqi', methods=['POST', 'OPTIONS'])
def get_aqi_endpoint():
    # Handle preflight request
    if request.method == 'OPTIONS':
        return '', 200
        
    try:

        data = request.get_json()    
        if not data:
            print("ERROR: No data provided")
            return jsonify({'error': 'No data provided'}), 400
        
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if latitude is None or longitude is None:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
        
        # Validate coordinates
        try:
            coords = ValidCoords(float(longitude), float(latitude))
        except Exception as e:
            return jsonify({'error': f'Invalid coordinates: {str(e)}'}), 400
        
        min_lon = coords.lon - BBOX
        max_lon = coords.lon + BBOX
        min_lat = coords.lat - BBOX
        max_lat = coords.lat + BBOX
        bbox = (min_lon, min_lat, max_lon, max_lat)
        
        #get date 
        date = datetime.now().date().strftime("%Y-%m-%d")
        aqi_data = get_aqi(bbox, date)
        
        response_data = {'aqi': aqi_data}
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f'ERROR: Exception occurred - {str(e)}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
    
#@app.route('/test', methods=['GET'])
#def test():
#    return jsonify({'message': 'Server is running!'}), 200

@app.route('/weather', methods='POST')
def get_weather(): 


    
if __name__ == "__main__":
    #print("=" * 50)
    #print("🚀 Starting Flask server on port 5001...")
    #print("=" * 50)
    app.run(debug=True, port=5001, host='127.0.0.1')