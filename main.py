"""
Main entry point for the ESP32 Sensor Station application.
...
"""

# Standard Library
import utime
import lvgl as lv  # LVGL muss hier importiert werden, falls display_setup es braucht

# Local Application
from ntp import set_rtc_from_ntp
from own_timers import start_timer_tasks
from system_tasks import run_system_tasks
from wifi import connect_wifi, is_connected

import display_setup  # Für die Hardware-Initialisierung
import display  # NEU: Das umbenannte Display-Modul


def main():
    """The main entry point and logic for the application."""
    print("--- Starting MicroPython ESP32 Sensor Station (LVGL) ---")

    # 1. Initialisierung des LVGL-Display-Treibers
    if not display_setup.init_display_driver():
        print("FATAL: Display-Hardwarefehler. System wird angehalten.")
        return

    # 2. LVGL UI-Objekte erstellen
    print("Erstelle LVGL-Benutzeroberfläche...")
    display.create_ui()  # Aufruf an das umbenannte Modul

    # 3. Initial Wi-Fi Connection
    connect_wifi()

    if not is_connected():
        print("FATAL: Initial WiFi connection failed. System wird angehalten.")
        return

    # 4. Initial NTP Time Synchronization
    print("Performing initial NTP synchronization...")
    set_rtc_from_ntp()

    # 5. Start Hardware Timer Tasks
    print("Starting hardware timer-based tasks...")
    start_timer_tasks()

    # 6. Main Application Loop
    print("Entering main application loop...")
    while True:
        run_system_tasks()

        # LVGL-Task-Handler muss regelmäßig ausgeführt werden
        lv.task_handler()

        # Sleep to prevent the loop from hogging the CPU
        utime.sleep_ms(50)


if __name__ == "__main__":
    main()
