# Standard Library
import gc

import lvgl as lv
import utime as time

# --- Globale Zustandsvariablen ---
weather_data = (None,) * 6
weather_icon_code = "01d"
current_icon_code = ""
current_wifi_status = None
main_screen = None

# Globale UI-Objekte
desc_label_obj, temp_label_obj, temp_value_obj = None, None, None
press_label_obj, press_value_obj, hum_label_obj, hum_value_obj = None, None, None, None
wind_label_obj, wind_value_obj, date_label_obj, time_label_obj = None, None, None, None
status_label_obj, weather_icon_img, wifi_icon_img = None, None, None

# --- UI Farben ---
COLOR_BG = 0x0A0E27
COLOR_CARD_BG = 0x1A1F3A
COLOR_PRIMARY = 0x00D9FF
COLOR_SECONDARY = 0x7B2FFF
COLOR_TEXT_PRIMARY = 0xFFFFFF
COLOR_TEXT_SECONDARY = 0xA0A0C0
COLOR_ACCENT = 0xFFB800


def set_weather_data(data, icon_code=None):
    """Setzt neue Wetterdaten (wird vom Timer aufgerufen)."""
    global weather_data, weather_icon_code
    weather_data = data
    if icon_code:
        weather_icon_code = icon_code


def create_card(parent, x, y, width, height):
    """Hilfsfunktion zum Erstellen einer UI-Karte."""
    card = lv.obj(parent)
    card.set_size(width, height)
    card.set_pos(x, y)
    card.set_style_bg_color(lv.color_hex(COLOR_CARD_BG), 0)
    card.set_style_radius(10, 0)
    card.set_style_border_width(0, 0)
    card.set_style_shadow_width(10, 0)
    card.set_style_shadow_opa(80, 0)
    card.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF) # Scrollbalken deaktivieren
    card.set_style_pad_all(0, 0) # Padding entfernen
    return card


def create_ui():
    """Erstellt die komplette Benutzeroberfläche."""
    global main_screen, desc_label_obj, temp_label_obj, temp_value_obj, press_label_obj
    global press_value_obj, hum_label_obj, hum_value_obj, wind_label_obj, wind_value_obj
    global date_label_obj, time_label_obj, weather_icon_img, wifi_icon_img

    main_screen = lv.obj()
    main_screen.set_style_bg_color(lv.color_hex(COLOR_BG), 0)
    lv.screen_load(main_screen)

    # --- Header: Datum & Zeit ---
    header_card = create_card(main_screen, 5, 5, 230, 60) # Höhe auf 60
    wifi_icon_img = lv.image(header_card)
    wifi_icon_img.set_src("S:/icons/wifi_off.bin")
    wifi_icon_img.align(lv.ALIGN.LEFT_MID, 0, 0)

    # Container für Zeit und Datum rechts vom Icon
    time_cont = lv.obj(header_card)
    time_cont.set_size(170, 58)
    time_cont.align(lv.ALIGN.RIGHT_MID, 0, 0)
    time_cont.set_style_bg_opa(0, 0)
    time_cont.set_style_border_width(0, 0)
    time_cont.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF) # Scrollbar auch hier deaktivieren

    date_label_obj = lv.label(time_cont)
    date_label_obj.set_text("--.--.----")
    date_label_obj.set_style_text_color(lv.color_hex(COLOR_TEXT_SECONDARY), 0)
    date_label_obj.center()
    date_label_obj.set_y(-12)

    time_label_obj = lv.label(time_cont)
    time_label_obj.set_text("--:--:--")
    time_label_obj.set_style_text_color(lv.color_hex(COLOR_PRIMARY), 0)
    time_label_obj.center()
    time_label_obj.set_y(12)


    # --- Status & Icons ---
    status_card = create_card(main_screen, 5, 70, 230, 80) # Y-Pos angepasst
    weather_icon_img = lv.image(status_card)
    weather_icon_img.set_src("S:/icons/01d.bin")
    weather_icon_img.align(lv.ALIGN.RIGHT_MID, -10, 0)

    desc_label_obj = lv.label(status_card)
    desc_label_obj.set_text("Lade...")
    desc_label_obj.set_style_text_color(lv.color_hex(COLOR_TEXT_SECONDARY), 0)
    desc_label_obj.align(lv.ALIGN.LEFT_MID, 10, 0)
    desc_label_obj.set_width(150)

    # --- Wetter-Kacheln ---
    row1_y = 155 # Y-Pos angepasst
    card_width = 110
    card_height = 80 # Höhe auf 80
    temp_card = create_card(main_screen, 5, row1_y, card_width, card_height)
    temp_label_obj = lv.label(temp_card)
    temp_label_obj.set_text("Temp")
    temp_label_obj.set_style_text_color(lv.color_hex(COLOR_ACCENT), 0)
    temp_label_obj.align(lv.ALIGN.TOP_MID, 0, 8) # Zentriert
    temp_value_obj = lv.label(temp_card)
    temp_value_obj.set_text("--°C")
    temp_value_obj.set_style_text_color(lv.color_hex(COLOR_TEXT_PRIMARY), 0)
    temp_value_obj.align(lv.ALIGN.TOP_MID, 0, 40) # Zentriert

    hum_card = create_card(main_screen, 125, row1_y, card_width, card_height)
    hum_label_obj = lv.label(hum_card)
    hum_label_obj.set_text("Humid")
    hum_label_obj.set_style_text_color(lv.color_hex(COLOR_PRIMARY), 0)
    hum_label_obj.align(lv.ALIGN.TOP_MID, 0, 8) # Zentriert
    hum_value_obj = lv.label(hum_card)
    hum_value_obj.set_text("--%")
    hum_value_obj.set_style_text_color(lv.color_hex(COLOR_TEXT_PRIMARY), 0)
    hum_value_obj.align(lv.ALIGN.TOP_MID, 0, 40) # Zentriert

    row2_y = 240 # Y-Pos angepasst
    wind_card = create_card(main_screen, 5, row2_y, card_width, card_height)
    wind_label_obj = lv.label(wind_card)
    wind_label_obj.set_text("Wind")
    wind_label_obj.set_style_text_color(lv.color_hex(COLOR_ACCENT), 0)
    wind_label_obj.align(lv.ALIGN.TOP_MID, 0, 8) # Zentriert
    wind_value_obj = lv.label(wind_card)
    wind_value_obj.set_text("--m/s")
    wind_value_obj.set_style_text_color(lv.color_hex(COLOR_TEXT_PRIMARY), 0)
    wind_value_obj.align(lv.ALIGN.TOP_MID, 0, 40) # Zentriert

    press_card = create_card(main_screen, 125, row2_y, card_width, card_height)
    press_label_obj = lv.label(press_card)
    press_label_obj.set_text("Bar")
    press_label_obj.set_style_text_color(lv.color_hex(COLOR_SECONDARY), 0)
    press_label_obj.align(lv.ALIGN.TOP_MID, 0, 8) # Zentriert
    press_value_obj = lv.label(press_card)
    press_value_obj.set_text("---hPa")
    press_value_obj.set_style_text_color(lv.color_hex(COLOR_TEXT_PRIMARY), 0)
    press_value_obj.align(lv.ALIGN.TOP_MID, 0, 40) # Zentriert

    print("✓ UI erstellt")
    oled_update_time()
    oled_update_weather()


def oled_update_time():
    """Aktualisiert die Uhrzeit."""
    if date_label_obj and time_label_obj:
        now = time.localtime()
        date_label_obj.set_text(f"{now[2]:02d}.{now[1]:02d}.{now[0]:04d}")
        time_label_obj.set_text(f"{now[3]:02d}:{now[4]:02d}:{now[5]:02d}")


def oled_update_weather():
    """Aktualisiert Wetterdaten und Icons (nur bei Änderung)."""
    global current_icon_code, current_wifi_status
    if not main_screen:
        return

    try:
        is_data_valid = weather_data and all(val is not None for val in weather_data)

        # Wetter-Icon
        new_icon = weather_icon_code if is_data_valid else "50d"
        if new_icon != current_icon_code:
            path = f"S:/icons/{new_icon}.bin"
            weather_icon_img.set_src(path)
            current_icon_code = new_icon
            print(f"✓ Wetter-Icon: {new_icon}")

        # WLAN-Icon
        new_wifi_status = "on" if is_data_valid else "off"
        if new_wifi_status != current_wifi_status:
            path = f"S:/icons/wifi_{new_wifi_status}.bin"
            wifi_icon_img.set_src(path)
            current_wifi_status = new_wifi_status
            print(f"✓ WLAN-Icon: {new_wifi_status}")

        # Text-Labels
        if is_data_valid:
            temp_value_obj.set_text(f"{weather_data[0]:.1f}°C")
            desc_label_obj.set_text(str(weather_data[5]))
            press_value_obj.set_text(f"{weather_data[1]}hPa")
            hum_value_obj.set_text(f"{weather_data[2]:.0f}%")
            wind_value_obj.set_text(f"{weather_data[3]:.1f}m/s")
        else:
            desc_label_obj.set_text("Keine Daten")
            temp_value_obj.set_text("--°C")
            press_value_obj.set_text("---hPa")
            hum_value_obj.set_text("--%")
            wind_value_obj.set_text("--m/s")

    except Exception as e:
        print(f"FEHLER in oled_update_weather: {e}")


def display_handler(timer=None):
    """Timer-Callback für alle Display-Updates."""
    try:
        gc.collect()
        oled_update_time()
        oled_update_weather()
        lv.refr_now(None)
    except Exception as e:
        print(f"FEHLER in display_handler: {e}")
