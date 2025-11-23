"""
Dieses Modul konfiguriert und startet die Hardware-Timer für periodische Aufgaben.
"""

# Third-Party
from machine import Timer

# Local Application
import display  # NEU: Import des umbenannten Moduls
import weather
import wifi


def weather_wrapper(timer):
    """
    Timer-Callback zur periodischen Aktualisierung der Wetterdaten.
    """

    owm_data = (None,) * 7  # Jetzt 7 Werte (mit icon_code)
    icon_code = None

    if wifi.is_connected():
        print("Task: Fetching weather data from API...")
        owm_data = weather.get_data()  # Gibt jetzt 7 Werte zurück

        # Icon-Code extrahieren (letzter Wert im Tuple)
        if owm_data and owm_data[6] is not None:
            icon_code = owm_data[6]
            owm_data = owm_data[:6]  # Nur die ersten 6 Werte für die Daten
        else:
            owm_data = (None,) * 6
            icon_code = None  # Sicherstellen, dass kein alter Icon-Code verwendet wird
    else:
        print("Task: Skipping weather data fetch, no WiFi.")
        owm_data = (None,) * 6
        icon_code = None

    # Den Zustand des Display-Moduls mit den neuen Daten und dem Icon-Code aktualisieren
    display.set_weather_data(owm_data, icon_code)


def start_timer_tasks():
    """
    Initialisiert und startet alle Hardware-Timer für die Anwendung.
    """
    # Führt eine erste Datenabfrage sofort beim Start durch
    print("Performing initial data fetch...")
    weather_wrapper(None)

    # Timer zum AKTUALISIEREN der LVGL-Anzeige (jede Sekunde für die Uhrzeit)
    display_timer = Timer(0)
    # Aufruf an das umbenannte Modul
    display_timer.init(
        period=1000, mode=Timer.PERIODIC, callback=display.display_handler
    )

    # Timer zum Holen von Wetterdaten (alle 15 Minuten)
    sensor_timer = Timer(1)
    sensor_timer.init(period=900000, mode=Timer.PERIODIC, callback=weather_wrapper)
