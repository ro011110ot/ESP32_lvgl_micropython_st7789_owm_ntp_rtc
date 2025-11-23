"""
Dieses Modul ist für das Abrufen und Verarbeiten von Wetterdaten von der OpenWeatherMap-API zuständig.
"""

import urequests

from secrets import secrets

# OpenWeatherMap API-Endpunkt und Konfiguration
API_URL = "http://api.openweathermap.org/data/2.5/weather?q={},{}&appid={}&units=metric&lang=de"

# API-Schlüssel und Standort aus der secrets.py-Datei
API_KEY = secrets["openweather_api_key"]
CITY = secrets["city"]
COUNTRY_CODE = secrets["country_code"]


def get_data():
    """
    Ruft die aktuellen Wetterdaten von der OpenWeatherMap-API ab.

    Returns:
        Ein Tuple mit den folgenden Wetterdaten:
        (Temperatur, Luftdruck, Luftfeuchtigkeit, Windgeschwindigkeit, Wetterbeschreibung, Hauptwetter, Icon-Code).
        Gibt (None, None, None, None, None, None, None) zurück, wenn ein Fehler auftritt.
    """
    url = API_URL.format(CITY, COUNTRY_CODE, API_KEY)

    try:
        print(f"Fetching weather data from: {url}")
        response = urequests.get(url)

        if response.status_code == 200:
            data = response.json()

            # Extrahieren der relevanten Daten aus der JSON-Antwort
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
        if "response" in locals() and response:
            response.close()
