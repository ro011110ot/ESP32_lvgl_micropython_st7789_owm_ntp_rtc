"""
This module is responsible for fetching and processing weather data from the OpenWeatherMap API.
"""

import urequests

from secrets import secrets

# OpenWeatherMap API endpoint and configuration
# The API_URL is formatted with city, country code, API key, units (metric), and language (English).
API_URL = "http://api.openweathermap.org/data/2.5/weather?q={},{}&appid={}&units=metric&lang=en"

# API key and location are loaded from the secrets.py file
API_KEY = secrets["openweather_api_key"]
CITY = secrets["city"]
COUNTRY_CODE = secrets["country_code"]


def get_data():
    """
    Fetches the current weather data from the OpenWeatherMap API.

    Constructs the API request URL using the configured city, country code,
    and API key. It then sends a GET request, parses the JSON response,
    and extracts relevant weather information.

    Returns:
        A tuple containing the following weather data:
        (temperature, pressure, humidity, wind_speed, description, main_weather, icon_code).
        Returns (None, None, None, None, None, None, None) if an error occurs
        during the API call or data parsing.
    """
    url = API_URL.format(CITY, COUNTRY_CODE, API_KEY)

    response = None  # Initialize response to None
    try:
        print(f"Fetching weather data from: {url}")
        response = urequests.get(url)

        if response.status_code == 200:
            data = response.json()

            # Extract relevant data from the JSON response
            temp = data.get("main", {}).get("temp")
            pressure = data.get("main", {}).get("pressure")
            humidity = data.get("main", {}).get("humidity")
            wind_speed = data.get("wind", {}).get("speed")

            weather_info = data.get("weather", [{}])[0]
            description = weather_info.get("description")
            main_weather = weather_info.get("main")
            icon_code = weather_info.get("icon")

            print("Weather data fetched successfully.")
            return (
                temp,
                pressure,
                humidity,
                wind_speed,
                description,
                main_weather,
                icon_code,
            )

        else:
            print(
                f"Error fetching weather data: HTTP Status Code {response.status_code}"
            )
            return (None,) * 7

    except Exception as e:
        print(f"An error occurred while fetching weather data: {e}")
        return (None,) * 7
    finally:
        if response:
            response.close()