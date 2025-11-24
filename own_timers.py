"""
This module configures and starts hardware timers for periodic tasks
within the ESP32 LVGL Weather Station application.
"""

from machine import Timer

import display
import weather
import wifi


def weather_wrapper(timer):
    """
    Timer callback for periodic weather data updates.

    This function fetches weather data from the OpenWeatherMap API if Wi-Fi is connected,
    then updates the display module with the new data and icon code.
    It's designed to be called by a hardware timer.

    Args:
        timer: The timer object that triggered this callback (not directly used).
    """
    owm_data = (None,) * 7  # Initialize with 7 None values (including icon_code)
    icon_code = None

    if wifi.is_connected():
        print("Task: Fetching weather data from API...")
        try:
            owm_data = weather.get_data()  # This should return 7 values
            # Extract icon code (last value in the tuple)
            if owm_data and owm_data[6] is not None:
                icon_code = owm_data[6]
                owm_data = owm_data[:6]  # Keep only the first 6 values for data
            else:
                owm_data = (None,) * 6
                icon_code = None  # Ensure no old icon code is used
        except Exception as e:
            print(f"ERROR: Failed to fetch weather data: {e}")
            owm_data = (None,) * 6
            icon_code = None
    else:
        print("Task: Skipping weather data fetch, no WiFi connection.")
        owm_data = (None,) * 6
        icon_code = None

    # Update the display module's state with the new data and icon code
    display.set_weather_data(owm_data, icon_code)


def start_timer_tasks():
    """
    Initializes and starts all hardware timers required for the application.

    - A 1-second periodic timer for updating the LVGL display (time, weather).
    - A 15-minute periodic timer for fetching new weather data.
    """
    # Perform an initial data fetch immediately upon startup
    print("Performing initial data fetch...")
    weather_wrapper(None)

    # Timer for updating the LVGL display (every second for clock updates)
    display_timer = Timer(0)
    display_timer.init(
        period=1000, mode=Timer.PERIODIC, callback=display.display_handler
    )
    print("✓ Display update timer started (1s interval).")

    # Timer for fetching weather data (every 15 minutes)
    weather_fetch_timer = Timer(1)
    weather_fetch_timer.init(period=900000, mode=Timer.PERIODIC, callback=weather_wrapper)
    print("✓ Weather fetch timer started (15min interval).")