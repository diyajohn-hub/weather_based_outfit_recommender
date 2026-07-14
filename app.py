from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import pickle
import requests

app = Flask(__name__)
CORS(app)


with open('outfit_model.pkl', 'rb') as file:
    model = pickle.load(file)


def get_coordinates(city_name):
    geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
    response = requests.get(geocode_url).json()
    
    if 'results' not in response:
        return None, None
    
    location = response['results'][0]
    return location['latitude'], location['longitude']


def get_live_weather(lat, lon):
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum,apparent_temperature_min,wind_speed_10m_max,apparent_temperature_max&timezone=auto&forecast_days=1"
    response = requests.get(weather_url).json()
    
    daily = response['daily']

    weather_data = {
        'precipitation_sum (mm)': daily['precipitation_sum'][0],
        'apparent_temperature_min (°C)': daily['apparent_temperature_min'][0],
        'wind_speed_10m_max (km/h)': daily['wind_speed_10m_max'][0],
        'apparent_temperature_max (°C)': daily['apparent_temperature_max'][0]
    }
    return weather_data


@app.route('/recommend', methods=['GET'])
def recommend_outfit():
    # 1. Capture all incoming parameters
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    city = request.args.get('city')
    
    # 2. Check: Do we have coordinates directly?
    if lat and lon:
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return jsonify({'error': 'Latitude and longitude must be valid decimals'}), 400
            
    # 3. If no coordinates, fallback to finding them via the City name
    elif city:
        lat, lon = get_coordinates(city)
        if lat is None:
            return jsonify({'error': f'Could not find coordinates for city: {city}'}), 404
            
    # 4. If neither coordinates nor city were provided, return an error
    else:
        return jsonify({'error': 'Please provide either a "city" parameter or both "lat" and "lon" parameters'}), 400
    
    # 5. Run prediction using resolved coordinates
    try:
        live_weather = get_live_weather(lat, lon)
        
        # Format weather data as a DataFrame for your ML model
        input_data = pd.DataFrame([live_weather])
        prediction = model.predict(input_data)[0]
        
        return jsonify({
            'city': city if city else f"GPS ({lat:.4f}, {lon:.4f})",
            'latitude': lat,
            'longitude': lon,
            'current_weather_metrics': live_weather,
            'recommended_outfit': prediction
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
   
    print("🚀 Outfit Recommender Backend Engine running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)