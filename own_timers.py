"""
This module configures and starts the hardware timers for periodic tasks.
"""

# Third-Party
from machine import Timer
from typing import Any

# Local Application
import data_logger
import display
import weather
import wifi


def weather_wrapper(timer: Any) -> None:
    """
    Timer callback for periodically updating and logging weather data.
    """
    owm_data = (None,) * 6
    if wifi.is_connected():
        print("Task: Fetching weather data from API...")
        owm_data = weather.get_data()
    else:
        print("Task: Skipping weather data fetch, no WiFi.")

    # Update the state of the display module with the new data
    display.set_weather_data(owm_data)

    # Log the data
    print("Task: Logging data...")
    data_logger.log_data(owm_data)


def start_timer_tasks() -> None:
    """
    Initializes and starts all hardware timers for the application.
    """
    # Perform an initial data fetch and log on startup
    print("Performing initial data fetch and log...")
    weather_wrapper(None)

    # Timer to UPDATE the LVGL display (every second for the time)
    display_timer = Timer(0)
    display_timer.init(
        period=1000, mode=Timer.PERIODIC, callback=display.display_handler
    )

    # Timer to fetch weather data (every 15 minutes)
    sensor_timer = Timer(1)
    sensor_timer.init(
        period=900000, mode=Timer.PERIODIC, callback=weather_wrapper
    )
