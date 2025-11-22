# ESP32 Weather and Sensor Monitoring Station

This project turns an ESP32 into a weather and sensor monitoring station. It reads temperature and humidity from a DHT11 sensor, fetches weather data from the OpenWeatherMap API, and displays the information on an OLED screen. The sensor and weather data are also logged to CSV files.

## Features

-   Connects to a Wi-Fi network.
-   Reads temperature and humidity from a DHT11 sensor.
-   Fetches current weather data from OpenWeatherMap.
-   Displays time, sensor data, and weather data on an OLED display.
-   Logs sensor and weather data to CSV files.
-   Switches between a time/sensor display and a weather display.

## File Descriptions

-   **`boot.py`**: This file is executed only once at boot-up. It is currently empty but can be used for special boot-time actions.
-   **`main.py`**: The main entry point of the application. It connects to Wi-Fi and starts the timers for sensor readings, weather updates, and display updates.
-   **`wifi.py`**: Handles the Wi-Fi connection. It connects to the network by trying a list of credentials stored in `secrets.py`.
-   **`ntp.py`**: Provides a function to get the current time from an NTP server and adjust it to Central European Time (CET/CEST) with daylight saving.
-   **`dht11.py`**: Reads temperature and humidity from the DHT11 sensor and logs the readings to a CSV file in the `/temp_history` directory.
-   **`weather.py`**: Fetches weather data from the OpenWeatherMap API using credentials from a `secrets.py` file (not included) and logs the data to a CSV file in the `/temp_history` directory.
-   **`oled.py`**: Manages the OLED display. It has functions to display the time, sensor data, and weather data. It also handles switching between the different display screens.
-   **`own_timers.py`**: Initializes and starts the timers that periodically trigger sensor readings, weather data fetching, and display updates.
-   **`temp_history/`**: This directory stores the CSV log files for temperature, humidity and weather data.

## Hardware Requirements

-   ESP32 development board
-   DHT11 temperature and humidity sensor
-   SSD1306 OLED display (I2C)
-   Breadboard and jumper wires

## Setup

1.  **Install MicroPython:** Flash your ESP32 with the latest version of MicroPython.
2.  **Install Libraries:** Connect to your ESP32's REPL and run the following commands to install the necessary library for the OLED display:
    '''python
    import mip
    mip.install("ssd1306")
    '''
3.  **Copy Files:** Copy all the project's `.py` files to the root directory of your ESP32.
4.  **Create `secrets.py`:** Create a file named `secrets.py` in the root directory with the following content. You can add multiple Wi-Fi networks to the `wifi_credentials` list. The system will try to connect to them in the order they are listed.
    '''python
    secrets = {
        "wifi_credentials": [
            {"ssid": "YOUR_FIRST_WIFI_SSID", "password": "YOUR_FIRST_WIFI_PASSWORD"},
            {"ssid": "YOUR_SECOND_WIFI_SSID", "password": "YOUR_SECOND_WIFI_PASSWORD"},
        ],
        "openweather_api_key": "YOUR_OPENWEATHERMAP_API_KEY",
        "city": "YOUR_CITY",
        "country_code": "YOUR_COUNTRY_CODE"
    }
    '''
5.  **Connect Hardware:** Connect the DHT11 sensor and the OLED display to your ESP32 according to the pin configurations in `dht11.py` and `oled.py`.
6.  **Run:** The `main.py` script will run automatically on boot.

## How it Works

The `main.py` script is the starting point. It first connects to the Wi-Fi network using the `wifi.py` module. Once connected, it calls `own_timers.start_timer()` to set up and start the timers.

There are two main timers:

1.  A timer that triggers every 5 seconds to switch the OLED display between the time/sensor view and the weather view.
2.  A timer that triggers every 15 minutes to read the DHT11 sensor and fetch new weather data from the OpenWeatherMap API.

The `oled.py` module is responsible for what is shown on the display. It uses global variables to access the latest sensor and weather data. These global variables are updated by the timer callbacks.

The `dht11.py` and `weather.py` modules not only provide the sensor and weather data but also log the data to CSV files in the `temp_history` directory. The files are named with the current date.# ESP32_lvgl_micropython_st7789_owm_ntp_rtc
