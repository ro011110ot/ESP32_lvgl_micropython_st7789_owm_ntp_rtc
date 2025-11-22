"""
This module provides a function to fetch weather data from the OpenWeatherMap API.
"""

# Third-Party
import urequests as requests

# Local Application
from secrets import secrets

# --- API Configuration ---
city = secrets["city"]
country_code = secrets["country_code"]
api_key = secrets["openweather_api_key"]

# Construct the URL with units=metric to get Celsius temperatures and m/s wind speed
open_weather_map_url = (
    f"http://api.openweathermap.org/data/2.5/weather?q="
    f"{city},{country_code}&APPID={api_key}&units=metric"
)


def get_data():
    """
    Fetches and parses weather data from the OpenWeatherMap API.

    Returns:
        A tuple containing (temp, pressure, humidity, wind_speed, wind_deg, weather_desc)
        on success, or a tuple of Nones on failure.
    """
    try:
        response = requests.get(open_weather_map_url)
        weather_json = response.json()
        response.close()

        # --- Parse the JSON response ---
        temp = weather_json["main"]["temp"]
        pressure = weather_json["main"]["pressure"]
        humidity = weather_json["main"]["humidity"]
        wind_speed = weather_json["wind"]["speed"]
        wind_deg = weather_json["wind"]["deg"]
        weather_desc = weather_json["weather"][0]["description"]

        print("Weather data successfully retrieved.")
        return temp, pressure, humidity, wind_speed, wind_deg, weather_desc

    except Exception as e:
        print(f"Error fetching/parsing weather data: {e}")
        # Return a tuple of Nones on failure to prevent crashes downstream
        return None, None, None, None, None, None
