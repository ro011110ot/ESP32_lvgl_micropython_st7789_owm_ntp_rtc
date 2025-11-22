"""
display.py - Komplette LVGL Display-Verwaltung für ESP32
display.py - Komplette LVGL Display-Verwaltung für ESP32 Wetterstation
Verwaltet die Benutzeroberfläche und aktualisiert Zeit- und Wetterdaten
"""

# Standard Library
import utime as time
import gc
import lvgl as lv

# --- Globale Variablen für den Zustand ---
weather_data = (None,) * 6
main_screen = None

# Globale Variablen für alle LVGL-Objekte
desc_label_obj = None
temp_label_obj = None
press_label_obj = None
hum_label_obj = None
wind_label_obj = None
date_label_obj = None
time_label_obj = None


def set_weather_data(data):
    """
    Setzt neue Wetterdaten und aktualisiert sofort die Anzeige.

    Args:
        data: Tuple mit (temp, pressure, humidity, wind, _, description)
    """
    global weather_data
    weather_data = data
    # Sofort anzeigen, nicht auf Timer warten
    oled_update_weather()


def create_ui():
    """
    Erstellt die komplette Benutzeroberfläche mit allen Labels.
    """
    global main_screen
    global desc_label_obj, temp_label_obj, press_label_obj, hum_label_obj, wind_label_obj
    global date_label_obj, time_label_obj

    # Hauptbildschirm erstellen
    main_screen = lv.obj()
    main_screen.set_style_bg_color(lv.color_hex(0x000000), 0)
    lv.screen_load(main_screen)

    # === DATUM LABEL ===
    date_label_obj = lv.label(main_screen)
    date_label_obj.set_text("--.--.----")
    date_label_obj.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
    date_label_obj.align(lv.ALIGN.TOP_MID, 0, 20)  # Von 5 auf 20 erhöht

    # === ZEIT LABEL ===
    time_label_obj = lv.label(main_screen)
    time_label_obj.set_text("--:--:--")
    time_label_obj.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
    time_label_obj.align(lv.ALIGN.TOP_MID, 0, 45)  # Von 30 auf 45 angepasst

    # === TRENNLINIE ===
    line = lv.obj(main_screen)
    line.set_size(lv.pct(90), 2)
    line.set_style_bg_color(lv.color_hex(0xAAAAAA), 0)
    line.set_style_border_width(0, 0)
    line.align(lv.ALIGN.TOP_MID, 0, 85)

    # === TITEL ===
    title_label = lv.label(main_screen)
    title_label.set_text("Wetter (OpenWeatherMap):")
    title_label.set_style_text_color(lv.color_hex(0x00AAFF), 0)
    title_label.align(lv.ALIGN.TOP_LEFT, 10, 100)

    # === WETTER-LABELS ===
    desc_label_obj = lv.label(main_screen)
    desc_label_obj.set_text("Lade Daten...")
    desc_label_obj.set_style_text_color(lv.color_hex(0xFFFF00), 0)

    temp_label_obj = lv.label(main_screen)
    temp_label_obj.set_text("Temperatur: ---")
    temp_label_obj.set_style_text_color(lv.color_hex(0xFFFFFF), 0)

    press_label_obj = lv.label(main_screen)
    press_label_obj.set_text("Druck: ---")
    press_label_obj.set_style_text_color(lv.color_hex(0xFFFFFF), 0)

    hum_label_obj = lv.label(main_screen)
    hum_label_obj.set_text("Feuchte: ---")
    hum_label_obj.set_style_text_color(lv.color_hex(0xFFFFFF), 0)

    wind_label_obj = lv.label(main_screen)
    wind_label_obj.set_text("Wind: ---")
    wind_label_obj.set_style_text_color(lv.color_hex(0xFFFFFF), 0)

    # Labels positionieren
    labels_list = [
        desc_label_obj,
        temp_label_obj,
        press_label_obj,
        hum_label_obj,
        wind_label_obj,
    ]

    y_pos = 130
    for label in labels_list:
        label.align(lv.ALIGN.TOP_LEFT, 10, y_pos)
        y_pos += 30

    gc.collect()

    # WICHTIG: Initiale Werte sofort setzen
    oled_update_time()
    oled_update_weather()

    # LVGL Task Handler einmal aufrufen
    lv.task_handler()


def oled_update_time():
    """
    Aktualisiert die Labels für Zeit und Datum.
    Wird jede Sekunde vom Timer aufgerufen.
    """
    if date_label_obj is None or time_label_obj is None:
        return

    try:
        now = time.localtime()
        date_str = f"{now[2]:02d}.{now[1]:02d}.{now[0]:04d}"
        time_str = f"{now[3]:02d}:{now[4]:02d}:{now[5]:02d}"

        date_label_obj.set_text(date_str)
        time_label_obj.set_text(time_str)

        # Display-Objekte als "dirty" markieren (neu zeichnen)
        date_label_obj.invalidate()
        time_label_obj.invalidate()

    except Exception as e:
        print(f"FEHLER in oled_update_time: {e}")


def oled_update_weather():
    """
    Aktualisiert die Labels für die Wetterdaten.
    Wird bei neuen Daten und vom Timer aufgerufen.
    """
    if main_screen is None or desc_label_obj is None:
        return

    try:
        data = weather_data

        # Prüfen ob alle Daten vorhanden sind
        if data and all(val is not None for val in data):
            # Format: (temp, pressure, humidity, wind, _, description)
            desc_label_obj.set_text(str(data[5]))
            temp_label_obj.set_text(f"Temperatur: {data[0]:.1f} °C")
            press_label_obj.set_text(f"Druck: {data[1]} hPa")
            hum_label_obj.set_text(f"Feuchte: {data[2]:.1f} %")
            wind_label_obj.set_text(f"Wind: {data[3]:.1f} m/s")

            # Alle Wetter-Labels als "dirty" markieren
            desc_label_obj.invalidate()
            temp_label_obj.invalidate()
            press_label_obj.invalidate()
            hum_label_obj.invalidate()
            wind_label_obj.invalidate()

        else:
            # Fallback wenn keine Daten verfügbar
            desc_label_obj.set_text("Keine Wetterdaten")
            temp_label_obj.set_text("Temperatur: ---")
            press_label_obj.set_text("Druck: WLAN pruefen")
            hum_label_obj.set_text("Feuchte: ---")
            wind_label_obj.set_text("Wind: ---")

    except Exception as e:
        print(f"FEHLER in oled_update_weather: {e}")
        if desc_label_obj:
            desc_label_obj.set_text(f"Fehler: {str(e)[:20]}")


def display_handler(timer=None):
    """
    Timer-Callback. Aktualisiert alle Daten auf dem Display.
    Wird jede Sekunde aufgerufen.

    Args:
        timer: Timer-Objekt (wird ignoriert)
    """
    try:
        oled_update_time()
        oled_update_weather()

        # KRITISCH: LVGL muss das Display neu zeichnen
        lv.refr_now(None)

    except Exception as e:
        print(f"FEHLER in display_handler: {e}")


def get_weather_data():
    """
    Gibt die aktuellen Wetterdaten zurück.

    Returns:
        Tuple mit (temp, pressure, humidity, wind, _, description)
    """
    return weather_data


def clear_display():
    """
    Setzt alle Anzeigen auf Standardwerte zurück.
    """
    global weather_data
    weather_data = (None,) * 6
    oled_update_weather()
    print("Display zurueckgesetzt")
