from flask import Flask, request, jsonify
from utils.data_getters import get_openmeteo_weather, rate_aqi, get_aqi 
from utils.dtypes import ValidCoords 
import datetime 

BBOX = 0.1

app = Flask(__name__)

@app.route("/aqi", methods=["POST"])
def get_realtime_aqi():
    try:
        # Get JSON data from the frontend
        data = request.get_json()
        lat = data.get("latitude")
        lon = data.get("longitude")

        in_coords = ValidCoords(latitude=lat, longitude=lon)
        min_lon = in_coords.lon - BBOX
        max_lon = in_coords.lon + BBOX
        min_lat = in_coords.lat - BBOX
        max_lat = in_coords.lat + BBOX
        bbox = (min_lon, min_lat, max_lon, max_lat)
        current_date = datetime.now().date()

        if lat is None or lon is None:
            return jsonify({"error": "Missing latitude or longitude"}), 400
        
        current_aqi = get_aqi(bbox, current_date)
        
        return jsonify({"AQI": current_aqi})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

    
if __name__ == "__main__":
    app.run(debug=True)

