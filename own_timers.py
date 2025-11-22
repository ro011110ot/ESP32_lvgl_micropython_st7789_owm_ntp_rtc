"""
Dieses Modul konfiguriert und startet die Hardware-Timer für periodische Aufgaben.
"""

# Third-Party
from machine import Timer

# Local Application
import data_logger
import display  # NEU: Import des umbenannten Moduls
import weather
import wifi


def weather_wrapper(timer):
    """
    Timer-Callback zur periodischen Aktualisierung der Wetterdaten und Protokollierung.
    """

    owm_data = (None,) * 6
    if wifi.is_connected():
        print("Task: Fetching weather data from API...")
        owm_data = weather.get_data()
    else:
        print("Task: Skipping weather data fetch, no WiFi.")

    # 2. Den Zustand des Display-Moduls mit den neuen Daten aktualisieren
    display.set_weather_data(owm_data)

    # 3. Daten protokollieren
    print("Task: Logging data...")
    data_logger.log_data(owm_data)


def start_timer_tasks():
    """
    Initialisiert und startet alle Hardware-Timer für die Anwendung.
    """
    # Führt eine erste Datenabfrage und Protokollierung sofort beim Start durch
    print("Performing initial data fetch and log...")
    weather_wrapper(None)

    # Timer zum AKTUALISIEREN der LVGL-Anzeige (jede Sekunde für die Uhrzeit)
    display_timer = Timer(0)
    # Aufruf an das umbenannte Modul
    display_timer.init(
        period=1000, mode=Timer.PERIODIC, callback=display.display_handler
    )

    # Timer zum Holen von Wetterdaten (alle 15 Minuten)
    sensor_timer = Timer(1)
    sensor_timer.init(
        period=900000, mode=Timer.PERIODIC, callback=weather_wrapper
    )
