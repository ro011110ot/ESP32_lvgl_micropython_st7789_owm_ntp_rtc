"""
This module provides a function to read temperature and humidity from a DHT11 sensor.
"""

# Third-Party
import dht
from machine import Pin

# --- Sensor Initialization ---
# Initialize the DHT11 sensor on GPIO pin 14
sensor = dht.DHT11(Pin(14))


def get_data():
    """Reads the DHT11 sensor after triggering a measurement.

    Returns:
        A tuple containing (temperature, humidity) on success,
        or (None, None) on failure.
    """
    try:
        sensor.measure()
        temp = sensor.temperature()  # In Celsius
        humi = sensor.humidity()     # In percent

        # Robust error handling for unreliable DHT readings
        if temp is None or humi is None:
            print("DHT sensor error: Could not read valid data.")
            return None, None

        return temp, humi

    except Exception as e:
        print(f"General DHT reading error: {e}")
        return None, None