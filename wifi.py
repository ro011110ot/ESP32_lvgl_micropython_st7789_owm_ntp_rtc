"""
This module handles the Wi-Fi connection for the ESP32.

It provides a robust connection function with retries and status LED feedback.
A global `wlan` object is used to allow other modules to check the connection status.
"""

# Standard Library
import time

# Third-Party
import network
from machine import Pin

# --- Global WLAN object ---
wlan = None

# --- Third-Party ---
from secrets import secrets

# --- LED Configuration ---
LED_PIN = 2
status_led = Pin(LED_PIN, Pin.OUT)


def flash_led(duration_ms, cycles, delay_ms):
    """Flashes the status LED for a specific number of cycles."""
    for _ in range(cycles):
        status_led.value(1)
        time.sleep_ms(duration_ms)
        status_led.value(0)
        time.sleep_ms(delay_ms)


def connect_wifi(max_retries=3, retry_delay_s=5, max_wait_s=10):
    """
    Connects to the Wi-Fi network with retries for robustness.
    It iterates through a list of predefined Wi-Fi credentials from secrets.py.

    Args:
        max_retries (int): The maximum number of connection attempts for each credential.
        retry_delay_s (int): The delay in seconds between retries.
        max_wait_s (int): The maximum time to wait for a single connection attempt.

    Returns:
        The network.WLAN object if successful, otherwise None.
    """
    global wlan
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    for credential in secrets["wifi_credentials"]:
        ssid = credential["ssid"]
        password = credential["password"]
        print(f"Attempting to connect to '{ssid}'...")

        for attempt in range(max_retries):
            print(f"  Attempt {attempt + 1}/{max_retries}...")

            try:
                wlan.connect(ssid, password)
            except OSError as e:
                print(f"    Connection command failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay_s)
                continue  # Go to next retry

            # Wait for connection, flashing the LED
            wait_cycles = int(max_wait_s * 1000 / 200)
            for _ in range(wait_cycles):
                if wlan.isconnected():
                    break
                flash_led(50, 1, 150)

            if wlan.isconnected():
                print(f"WiFi connected successfully to '{ssid}'.")
                flash_led(500, 3, 500)  # Success signal
                status_led.value(0)
                return wlan
            else:
                print("    Connection attempt failed.")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay_s)

        wlan.disconnect()
        time.sleep_ms(500)

    print(f"Failed to connect to any WiFi network after trying all credentials.")
    flash_led(100, 5, 100)  # Failure signal
    status_led.value(0)
    wlan = None
    return None


def is_connected():
    """Checks if the Wi-Fi is currently connected."""
    if wlan is None:
        return False
    return wlan.isconnected()
