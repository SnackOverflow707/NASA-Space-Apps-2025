from flask import Flask, jsonify
from earthdata_access import login, get_data

app = Flask(__name__)
auth = login()  # authenticate once at app startup

@app.route("/get_data")
def data_route():
    return get_data(auth)
import requests

# Example API endpoint 1: Latest SpaceX launch
@app.route("/api/latest_launch")
def latest_launch():
    url = "https://api.spacexdata.com/v5/launches/latest"  # replace with your own API
    data = requests.get(url).json()
    return jsonify({
        "name": data.get("name", "N/A"),
        "date": data.get("date_utc", "N/A")
    })

# Example API endpoint 2: Health check
@app.route("/api/ping")
def ping():
    return jsonify({"status": "ok"})

# Example API endpoint 3: Another external API (e.g., NASA APOD)
@app.route("/api/nasa_apod")
def nasa_apod():
    url = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"
    data = requests.get(url).json()
    return jsonify({
        "title": data.get("title", "N/A"),
        "image_url": data.get("url", "N/A"),
        "explanation": data.get("explanation", "N/A")
    })

if __name__ == "__main__":
    app.run(debug=True)

