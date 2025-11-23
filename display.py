# Standard Library
import gc

import lvgl as lv
import utime as time

# --- Globale Variablen für den Zustand ---
weather_data = (None,) * 6
weather_icon_code = "01d"  # OWM Icon-Code
main_screen = None

# Globale Variablen für alle LVGL-Objekte
desc_label_obj = None
temp_label_obj = None
temp_value_obj = None
press_label_obj = None
press_value_obj = None
hum_label_obj = None
hum_value_obj = None
wind_label_obj = None
wind_value_obj = None
date_label_obj = None
time_label_obj = None
status_label_obj = None
weather_icon_img = None
wifi_icon_img = None

# Display-Dimensionen
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 320
COLOR_BG = 0x0A0E27
COLOR_CARD_BG = 0x1A1F3A
COLOR_PRIMARY = 0x00D9FF
COLOR_SECONDARY = 0x7B2FFF
COLOR_TEXT_PRIMARY = 0xFFFFFF
COLOR_TEXT_SECONDARY = 0xA0A0C0
COLOR_ACCENT = 0xFFB800
COLOR_SUCCESS = 0x00FF9D
COLOR_WARNING = 0xFF6B00


def set_weather_data(data, icon_code=None):
    """
    Setzt neue Wetterdaten und Icon-Code.

    Args:
        data: Tuple mit (temp, pressure, humidity, wind, _, description)
        icon_code: OWM Icon-Code (z.B. "10d"), optional
    """
    global weather_data, weather_icon_code
    weather_data = data

    # Icon-Code aus API-Daten aktualisieren
    if icon_code:
        weather_icon_code = icon_code
        print(f"DEBUG: Icon-Code auf {icon_code} gesetzt")

    oled_update_weather()


def create_card(parent, x, y, width, height):
    """
    Erstellt eine Karte mit abgerundeten Ecken und Schatten-Effekt.
    """
    card = lv.obj(parent)
    card.set_size(width, height)
    card.set_pos(x, y)
    card.set_style_bg_color(lv.color_hex(COLOR_CARD_BG), 0)
    card.set_style_bg_opa(255, 0)
    card.set_style_radius(10, 0)
    card.set_style_border_width(0, 0)
    card.set_style_shadow_width(10, 0)
    card.set_style_shadow_color(lv.color_hex(0x000000), 0)
    card.set_style_shadow_opa(80, 0)
    card.set_style_pad_all(0, 0)
    return card


def create_ui():
    """
    Erstellt die Benutzeroberfläche im neuen Layout.

    Layout:
    ┌──────────────────────────┐
    │        Datum             │
    │        Zeit              │
    ├──────────────────────────┤
    │ [Status]    [Icon]       │
    ├────────────┬─────────────┤
    │ Temp       │ Humid       │
    ├────────────┼─────────────┤
    │ Wind       │ Bar         │
    └────────────┴─────────────┘
    """
    global main_screen
    global desc_label_obj, temp_label_obj, temp_value_obj
    global press_label_obj, press_value_obj, hum_label_obj, hum_value_obj
    global wind_label_obj, wind_value_obj
    global date_label_obj, time_label_obj, status_label_obj, weather_icon_img, wifi_icon_img

    main_screen = lv.obj()
    main_screen.set_style_bg_color(lv.color_hex(COLOR_BG), 0)
    main_screen.set_style_bg_grad_color(lv.color_hex(0x1A1F3A), 0)
    main_screen.set_style_bg_grad_dir(lv.GRAD_DIR.VER, 0)
    lv.screen_load(main_screen)

    # === HEADER: DATUM & ZEIT ===
    header_card = create_card(main_screen, 5, 5, 230, 55)

    # Datum (mittig)
    date_label_obj = lv.label(header_card)
    date_label_obj.set_text("--.--.----")
    date_label_obj.set_style_text_color(lv.color_hex(COLOR_TEXT_SECONDARY), 0)
    date_label_obj.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
    date_label_obj.set_width(210)
    date_label_obj.set_pos(10, 8)

    # Zeit (mittig, größer)
    time_label_obj = lv.label(header_card)
    time_label_obj.set_text("--:--:--")
    time_label_obj.set_style_text_color(lv.color_hex(COLOR_PRIMARY), 0)
    time_label_obj.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
    time_label_obj.set_width(210)
    time_label_obj.set_pos(10, 30)

    # === STATUS & WETTER-ICON ===
    status_card = create_card(main_screen, 5, 65, 230, 70)

    # WLAN Icon (links oben)
    global wifi_icon_img
    try:
        wifi_icon_img = lv.image(status_card)
    except AttributeError:
        try:
            wifi_icon_img = lv.img(status_card)
        except AttributeError:
            wifi_icon_img = None

    if wifi_icon_img:
        try:
            wifi_icon_img.set_src("S:/icons/wifi_off.png")  # Mit Drive-Letter!
            wifi_icon_img.set_pos(8, 8)
            wifi_icon_img.set_size(32, 32)  # Größe explizit setzen
            print("✓ WLAN-Icon gesetzt")
        except Exception as e:
            print(f"✗ WLAN-Icon-Fehler: {e}")

    # Wetter-Beschreibung (unter WLAN-Icon)
    desc_label_obj = lv.label(status_card)
    desc_label_obj.set_text("Lade...")
    desc_label_obj.set_style_text_color(lv.color_hex(COLOR_TEXT_SECONDARY), 0)
    desc_label_obj.set_pos(8, 45)
    desc_label_obj.set_width(130)

    # Wetter-Icon (rechts) - mit lv.image für LVGL 9.x
    try:
        weather_icon_img = lv.image(status_card)
        print("✓ lv.image verwendet")
    except AttributeError:
        try:
            weather_icon_img = lv.img(status_card)
            print("✓ lv.img verwendet")
        except AttributeError:
            print("✗ Weder lv.image noch lv.img verfügbar!")
            weather_icon_img = None

    if weather_icon_img:
        # Icon laden und positionieren
        try:
            weather_icon_img.set_src("S:/icons/01d.png")  # PNG statt BIN!
            weather_icon_img.set_pos(160, 5)
            weather_icon_img.set_size(60, 60)
            print("✓ Icon gesetzt")
        except Exception as e:
            print(f"✗ Icon-Fehler: {e}")

    # === ZEILE 1: TEMP & HUMID ===
    row1_y = 145
    card_width = 110

    # Temperatur (links)
    temp_card = create_card(main_screen, 5, row1_y, card_width, 65)
    temp_label_obj = lv.label(temp_card)
    temp_label_obj.set_text("Temp")
    temp_label_obj.set_style_text_color(lv.color_hex(COLOR_ACCENT), 0)
    temp_label_obj.set_pos(8, 6)

    temp_value_obj = lv.label(temp_card)
    temp_value_obj.set_text("--°C")
    temp_value_obj.set_style_text_color(lv.color_hex(COLOR_TEXT_PRIMARY), 0)
    temp_value_obj.set_pos(8, 32)
    temp_value_obj.set_width(card_width - 16)
    # Text-Modus: dot statt CLIP in LVGL 9.x
    try:
        temp_value_obj.set_long_mode(lv.label.LONG.DOT)
    except:
        pass  # Falls nicht verfügbar

    # Luftfeuchtigkeit (rechts)
    hum_card = create_card(main_screen, 125, row1_y, card_width, 65)
    hum_label_obj = lv.label(hum_card)
    hum_label_obj.set_text("Humid")
    hum_label_obj.set_style_text_color(lv.color_hex(COLOR_PRIMARY), 0)
    hum_label_obj.set_pos(8, 6)

    hum_value_obj = lv.label(hum_card)
    hum_value_obj.set_text("--%")
    hum_value_obj.set_style_text_color(lv.color_hex(COLOR_TEXT_PRIMARY), 0)
    hum_value_obj.set_pos(8, 32)
    hum_value_obj.set_width(card_width - 16)
    try:
        hum_value_obj.set_long_mode(lv.label.LONG.DOT)
    except:
        pass

    # === ZEILE 2: WIND & BAR ===
    row2_y = 220

    # Wind (links)
    wind_card = create_card(main_screen, 5, row2_y, card_width, 65)
    wind_label_obj = lv.label(wind_card)
    wind_label_obj.set_text("Wind")
    wind_label_obj.set_style_text_color(lv.color_hex(COLOR_ACCENT), 0)
    wind_label_obj.set_pos(8, 6)

    wind_value_obj = lv.label(wind_card)
    wind_value_obj.set_text("--m/s")
    wind_value_obj.set_style_text_color(lv.color_hex(COLOR_TEXT_PRIMARY), 0)
    wind_value_obj.set_pos(8, 32)
    wind_value_obj.set_width(card_width - 16)
    try:
        wind_value_obj.set_long_mode(lv.label.LONG.DOT)
    except:
        pass

    # Luftdruck (rechts)
    press_card = create_card(main_screen, 125, row2_y, card_width, 65)
    press_label_obj = lv.label(press_card)
    press_label_obj.set_text("Bar")
    press_label_obj.set_style_text_color(lv.color_hex(COLOR_SECONDARY), 0)
    press_label_obj.set_pos(8, 6)

    press_value_obj = lv.label(press_card)
    press_value_obj.set_text("---hPa")
    press_value_obj.set_style_text_color(lv.color_hex(COLOR_TEXT_PRIMARY), 0)
    press_value_obj.set_pos(8, 32)
    press_value_obj.set_width(card_width - 16)
    try:
        press_value_obj.set_long_mode(lv.label.LONG.DOT)
    except:
        pass

    gc.collect()
    print("✓ UI mit neuem Layout erstellt")

    oled_update_time()
    oled_update_weather()
    lv.task_handler()


def oled_update_time():
    """
    Aktualisiert Zeit und Datum.
    """
    if date_label_obj is None or time_label_obj is None:
        return

    try:
        now = time.localtime()
        date_str = f"{now[2]:02d}.{now[1]:02d}.{now[0]:04d}"
        time_str = f"{now[3]:02d}:{now[4]:02d}:{now[5]:02d}"

        date_label_obj.set_text(date_str)
        time_label_obj.set_text(time_str)

        date_label_obj.invalidate()
        time_label_obj.invalidate()

    except Exception as e:
        print(f"FEHLER in oled_update_time: {e}")


def oled_update_weather():
    """
    Aktualisiert Wetterdaten mit OWM Icon-Bild.
    """
    if main_screen is None or desc_label_obj is None:
        return

    # 1. Speicher VOR dem Update aufräumen
    gc.collect()

    try:
        data = weather_data

        if data and all(val is not None for val in data):
            # Icon-Pfad setzen (mit Drive-Letter S:)
            icon_path = f"S:/icons/{weather_icon_code}.png"

            if weather_icon_img:
                try:
                    weather_icon_img.set_src(icon_path)
                    print(f"✓ Icon geladen: {icon_path}")
                except Exception as e:
                    print(f"✗ Icon-Ladefehler ({icon_path}): {e}")

            # Wetterdaten aktualisieren
            temp_value_obj.set_text(f"{data[0]:.1f}°C")
            desc_label_obj.set_text(str(data[5]))
            press_value_obj.set_text(f"{data[1]}hPa")
            hum_value_obj.set_text(f"{data[2]:.0f}%")
            wind_value_obj.set_text(f"{data[3]:.1f}m/s")

            # WLAN-Icon auf "verbunden" setzen (mit Drive-Letter)
            if wifi_icon_img:
                try:
                    wifi_icon_img.set_src("S:/icons/wifi_on.png")
                except Exception as e:
                    print(f"✗ WLAN-Icon Update-Fehler: {e}")

            # Invalidieren
            if weather_icon_img:
                weather_icon_img.invalidate()
            if wifi_icon_img:
                wifi_icon_img.invalidate()
            desc_label_obj.invalidate()
            temp_value_obj.invalidate()
            press_value_obj.invalidate()
            hum_value_obj.invalidate()
            wind_value_obj.invalidate()

        else:
            # Keine Daten verfügbar
            if weather_icon_img:
                try:
                    weather_icon_img.set_src("S:/icons/50d.png")
                except:
                    pass

            # WLAN-Icon auf "getrennt" setzen
            if wifi_icon_img:
                try:
                    wifi_icon_img.set_src("S:/icons/wifi_off.png")
                except:
                    pass

            desc_label_obj.set_text("Keine Daten")
            temp_value_obj.set_text("--°C")
            press_value_obj.set_text("---hPa")
            hum_value_obj.set_text("--%")
            wind_value_obj.set_text("--m/s")

    except Exception as e:
        print(f"FEHLER in oled_update_weather: {e}")
        # WLAN-Icon auf Fehler setzen
        if wifi_icon_img:
            try:
                wifi_icon_img.set_src("S:/icons/wifi_off.png")
            except:
                pass


def display_handler(timer=None):
    """
    Timer-Callback für Display-Updates.
    """
    try:
        # Speicher aufräumen bevor LVGL versucht zu zeichnen
        gc.collect()
        oled_update_time()
        oled_update_weather()
        lv.refr_now(None)

    except Exception as e:
        print(f"FEHLER in display_handler: {e}")


def get_weather_data():
    """
    Gibt aktuelle Wetterdaten zurück.
    """
    return weather_data


def clear_display():
    """
    Setzt Display zurück.
    """
    global weather_data, weather_icon_code
    weather_data = (None,) * 6
    weather_icon_code = "01d"
    oled_update_weather()
    print("Display zurückgesetzt")
