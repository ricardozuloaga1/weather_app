import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
import requests
import urllib.parse
import random

# Load environment variables from .env file
load_dotenv()

# Assign variables
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')

# Strip any leading/trailing whitespace
if WEATHER_API_KEY:
    WEATHER_API_KEY = WEATHER_API_KEY.strip()

if PEXELS_API_KEY:
    PEXELS_API_KEY = PEXELS_API_KEY.strip()

# Check if API keys are available
if WEATHER_API_KEY is None or WEATHER_API_KEY == "":
    raise Exception("OpenWeatherMap API key is not set.")

if PEXELS_API_KEY is None or PEXELS_API_KEY == "":
    raise Exception("Pexels API key is not set.")

# Initialize Flask app
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    city = 'New York'  # Default city
    error_message = None
    weather_data = None
    clothing_images = []

    if request.method == 'POST':
        city = request.form.get('city')

    weather_data = get_weather_data(city)
    if weather_data:
        weather_condition = weather_data['weather'][0]['main']
        temperature = weather_data['main']['temp']
        clothing_images = get_clothing_images(weather_condition, city, temperature)
    else:
        error_message = "Could not retrieve weather data."

    return render_template('index.html', city=city, weather=weather_data, images=clothing_images, error_message=error_message)

def get_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching weather data: {response.status_code} - {response.text}")
        return None

def get_clothing_images(weather_condition, city, temperature):
    condition_mappings = {
        'Clear': 'sunny',
        'Clouds': 'cloudy',
        'Rain': 'rainy',
        'Drizzle': 'drizzle',
        'Thunderstorm': 'stormy',
        'Snow': 'snowy',
        'Mist': 'mist',
        'Fog': 'foggy',
        'Haze': 'hazy',
        'Smoke': 'smoky',
    }
    search_term = condition_mappings.get(weather_condition, weather_condition)
    
    # Determine if the weather is hot or cold based on temperature
    if temperature > 25:
        temperature_term = 'hot'
    elif temperature < 10:
        temperature_term = 'cold'
    else:
        temperature_term = 'mild'
    
    query = f"{temperature_term} {search_term} clothing in {city}"
    url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=20"  # Request more images
    headers = {
        "Authorization": PEXELS_API_KEY,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    print(f"Requesting URL: {url}")  # Debugging statement
    print(f"Response Status Code: {response.status_code}")  # Debugging statement
    print(f"Response Text: {response.text}")  # Debugging statement
    if response.status_code == 200:
        try:
            data = response.json()
            if data['total_results'] > 0:
                image_urls = [photo['src']['medium'] for photo in data['photos']]
                random.shuffle(image_urls)  # Shuffle the list of images
                return image_urls[:5]  # Return a subset of images
            else:
                print("No images found for the given weather condition.")
                return []
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            return []
    else:
        print(f"Error fetching images: {response.status_code} - {response.text}")
        return []

if __name__ == '__main__':
    app.run(debug=True)