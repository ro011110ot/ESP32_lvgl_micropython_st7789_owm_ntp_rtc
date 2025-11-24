"""
This module handles the Wi-Fi connection for the ESP32.

It provides a robust connection function with retries and status LED feedback.
A global `wlan` object is used to allow other modules to check the connection status.
"""

import time

import network
from machine import Pin

from secrets import secrets

# --- Global WLAN object ---
# This object holds the Wi-Fi station interface once initialized.
wlan = None

# --- LED Configuration ---
# Pin number for the status LED. This is typically the onboard LED.
LED_PIN = 2
status_led = Pin(LED_PIN, Pin.OUT)


def flash_led(duration_ms: int, cycles: int, delay_ms: int) -> None:
    """
    Flashes the status LED for a specific number of cycles.

    Args:
        duration_ms (int): The duration in milliseconds the LED stays on for each flash.
        cycles (int): The number of times the LED should flash.
        delay_ms (int): The delay in milliseconds between flashes.
    """
    for _ in range(cycles):
        status_led.value(1)  # Turn LED on
        time.sleep_ms(duration_ms)
        status_led.value(0)  # Turn LED off
        time.sleep_ms(delay_ms)


def connect_wifi(max_retries: int = 3, retry_delay_s: int = 5, max_wait_s: int = 10):
    """
    Connects to a Wi-Fi network with retries for robustness.

    It iterates through a list of predefined Wi-Fi credentials from `secrets.py`.
    For each credential, it attempts to connect multiple times.

    Args:
        max_retries (int): The maximum number of connection attempts for each credential.
        retry_delay_s (int): The delay in seconds between retries for the same credential.
        max_wait_s (int): The maximum time to wait for a single connection attempt to succeed.

    Returns:
        network.WLAN: The `network.WLAN` object if successfully connected, otherwise `None`.
    """
    global wlan
    wlan = network.WLAN(network.STA_IF)  # Create a station interface
    wlan.active(True)  # Activate the interface

    for credential in secrets["wifi_credentials"]:
        ssid = credential["ssid"]
        password = credential["password"]
        print(f"Attempting to connect to '{ssid}'...")

        for attempt in range(max_retries):
            print(f"  Attempt {attempt + 1}/{max_retries} for '{ssid}'...")

            try:
                wlan.connect(ssid, password)
            except OSError as e:
                print(f"    Connection command failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay_s)
                continue  # Skip to the next retry for this credential

            # Wait for connection, providing visual feedback with the LED
            wait_cycles = int(max_wait_s * 1000 / 200)  # Calculate LED flash cycles
            for _ in range(wait_cycles):
                if wlan.isconnected():
                    break
                flash_led(50, 1, 150)  # Short flash while waiting

            if wlan.isconnected():
                print(f"WiFi connected successfully to '{ssid}'. IP: {wlan.ifconfig()[0]}")
                flash_led(500, 3, 500)  # Long flashes for success
                status_led.value(0)  # Ensure LED is off after success
                return wlan
            else:
                print(f"    Connection attempt to '{ssid}' failed.")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay_s)

        # If all retries for the current credential failed, disconnect and try the next one
        wlan.disconnect()
        time.sleep_ms(500)

    print("Failed to connect to any WiFi network after trying all credentials.")
    flash_led(100, 5, 100)  # Rapid flashes for complete failure
    status_led.value(0)  # Ensure LED is off after failure
    wlan = None  # Reset wlan object on complete failure
    return None


def is_connected() -> bool:
    """
    Checks if the Wi-Fi interface is currently connected to an access point.

    Returns:
        bool: True if connected, False otherwise.
    """
    if wlan is None:
        return False
    return wlan.isconnected()