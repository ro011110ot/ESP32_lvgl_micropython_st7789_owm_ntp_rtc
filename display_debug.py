"""
display.py - Complete LVGL Display Management for ESP32 Weather Station
Manages the user interface and updates time and weather data.
"""

# Standard Library
import utime as time
import gc
import lvgl as lv
from typing import Tuple, Optional, Any

# --- Global State Variables ---
weather_data: Tuple[Optional[float], ...] = (None,) * 6
main_screen: Optional[lv.obj] = None

# Global variables for all LVGL objects
desc_label_obj: Optional[lv.label] = None
temp_label_obj: Optional[lv.label] = None
press_label_obj: Optional[lv.label] = None
hum_label_obj: Optional[lv.label] = None
wind_label_obj: Optional[lv.label] = None
date_label_obj: Optional[lv.label] = None
time_label_obj: Optional[lv.label] = None


def set_weather_data(data: Tuple[Optional[float], ...]) -> None:
    """
    Sets new weather data and immediately updates the display.

    Args:
        data: Tuple with (temp, pressure, humidity, wind, _, description)
    """
    global weather_data
    weather_data = data
    print(f"DEBUG: Weather data set: {data}")
    # Update display immediately, don't wait for the timer
    oled_update_weather()


def create_ui() -> None:
    """
    Creates the complete user interface with all labels.
    """
    global main_screen
    global desc_label_obj, temp_label_obj, press_label_obj, hum_label_obj, wind_label_obj
    global date_label_obj, time_label_obj

    print("Creating LVGL UI...")

    # Create main screen
    main_screen = lv.obj()
    main_screen.set_style_bg_color(lv.color_hex(0x000000), 0)
    lv.screen_load(main_screen)

    # === DATE LABEL ===
    date_label_obj = lv.label(main_screen)
    date_label_obj.set_text("--.--.----")
    date_label_obj.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
    date_label_obj.align(lv.ALIGN.TOP_MID, 0, 20)  # Increased from 5 to 20

    # === TIME LABEL ===
    time_label_obj = lv.label(main_screen)
    time_label_obj.set_text("--:--:--")
    time_label_obj.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
    time_label_obj.align(lv.ALIGN.TOP_MID, 0, 45)  # Adjusted from 30 to 45

    # === SEPARATOR LINE ===
    line = lv.obj(main_screen)
    line.set_size(lv.pct(90), 2)
    line.set_style_bg_color(lv.color_hex(0xAAAAAA), 0)
    line.set_style_border_width(0, 0)
    line.align(lv.ALIGN.TOP_MID, 0, 85)

    # === TITLE ===
    title_label = lv.label(main_screen)
    title_label.set_text("Weather (OpenWeatherMap):")
    title_label.set_style_text_color(lv.color_hex(0x00AAFF), 0)
    title_label.align(lv.ALIGN.TOP_LEFT, 10, 100)

    # === WEATHER LABELS ===
    desc_label_obj = lv.label(main_screen)
    desc_label_obj.set_text("Loading data...")
    desc_label_obj.set_style_text_color(lv.color_hex(0xFFFF00), 0)

    temp_label_obj = lv.label(main_screen)
    temp_label_obj.set_text("Temperature: ---")
    temp_label_obj.set_style_text_color(lv.color_hex(0xFFFFFF), 0)

    press_label_obj = lv.label(main_screen)
    press_label_obj.set_text("Pressure: ---")
    press_label_obj.set_style_text_color(lv.color_hex(0xFFFFFF), 0)

    hum_label_obj = lv.label(main_screen)
    hum_label_obj.set_text("Humidity: ---")
    hum_label_obj.set_style_text_color(lv.color_hex(0xFFFFFF), 0)

    wind_label_obj = lv.label(main_screen)
    wind_label_obj.set_text("Wind: ---")
    wind_label_obj.set_style_text_color(lv.color_hex(0xFFFFFF), 0)

    # Position labels
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

    # IMPORTANT: Set initial values immediately
    print("Setting initial values...")
    oled_update_time()
    oled_update_weather()

    # Call LVGL task handler once
    lv.task_handler()

    print("UI creation completed.")


def oled_update_time() -> None:
    """
    Updates the time and date labels.
    Called every second by the timer.
    """
    if date_label_obj is None or time_label_obj is None:
        print("DEBUG: Time labels are None!")
        return

    try:
        now = time.localtime()
        date_str = f"{now[2]:02d}.{now[1]:02d}.{now[0]:04d}"
        time_str = f"{now[3]:02d}:{now[4]:02d}:{now[5]:02d}"

        date_label_obj.set_text(date_str)
        time_label_obj.set_text(time_str)

        # Mark display objects as "dirty" (redraw)
        date_label_obj.invalidate()
        time_label_obj.invalidate()

        # Debug only every 10 seconds
        if now[5] % 10 == 0:
            print(f"DEBUG: Time updated: {date_str} {time_str}")

    except Exception as e:
        print(f"ERROR in oled_update_time: {e}")


def oled_update_weather() -> None:
    """
    Updates the weather data labels.
    Called when new data is available and by the timer.
    """
    if main_screen is None or desc_label_obj is None:
        print("DEBUG: Weather labels are None!")
        return

    try:
        data = weather_data

        # Check if all data is available
        if data and all(val is not None for val in data):
            # Format: (temp, pressure, humidity, wind, _, description)
            desc_label_obj.set_text(str(data[5]))
            temp_label_obj.set_text(f"Temperature: {data[0]:.1f} °C")
            press_label_obj.set_text(f"Pressure: {data[1]} hPa")
            hum_label_obj.set_text(f"Humidity: {data[2]:.1f} %")
            wind_label_obj.set_text(f"Wind: {data[3]:.1f} m/s")

            # Mark all weather labels as "dirty"
            desc_label_obj.invalidate()
            temp_label_obj.invalidate()
            press_label_obj.invalidate()
            hum_label_obj.invalidate()
            wind_label_obj.invalidate()

            print(f"DEBUG: Weather updated - {data[0]:.1f}°C, {data[5]}")
        else:
            # Fallback if no data is available
            desc_label_obj.set_text("No weather data")
            temp_label_obj.set_text("Temperature: ---")
            press_label_obj.set_text("Pressure: Check WLAN")
            hum_label_obj.set_text("Humidity: ---")
            wind_label_obj.set_text("Wind: ---")

            print("DEBUG: No valid weather data available")

    except Exception as e:
        print(f"ERROR in oled_update_weather: {e}")
        desc_label_obj.set_text(f"Error: {str(e)[:20]}")


def display_handler(timer: Optional[Any] = None) -> None:
    """
    Timer callback. Updates all data on the display.
    Called every second.

    Args:
        timer: Timer object (ignored)
    """
    try:
        oled_update_time()
        oled_update_weather()

        # CRITICAL: LVGL needs to redraw the display
        lv.refr_now(None)

    except Exception as e:
        print(f"ERROR in display_handler: {e}")


def get_weather_data() -> Tuple[Optional[float], ...]:
    """
    Returns the current weather data.

    Returns:
        Tuple with (temp, pressure, humidity, wind, _, description)
    """
    return weather_data


def clear_display() -> None:
    """
    Resets all display elements to their default values.
    """
    global weather_data
    weather_data = (None,) * 6
    oled_update_weather()
    print("Display reset")
