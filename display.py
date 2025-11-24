"""
display.py - LVGL User Interface Management

This module is responsible for creating, managing, and updating all elements
of the LVGL-based user interface for the weather station.
"""

import gc
import sys
import utime as time

import lvgl as lv

# --- UI Colors ---
COLOR_BG = 0x0A0E27
COLOR_CARD_BG = 0x1A1F3A
COLOR_PRIMARY = 0x00D9FF
COLOR_SECONDARY = 0x7B2FFF
COLOR_TEXT_PRIMARY = 0xFFFFFF
COLOR_TEXT_SECONDARY = 0xA0A0C0
COLOR_ACCENT = 0xFFB800

# --- Global State ---
# These variables hold the data to be displayed.
weather_data = (None,) * 6
weather_icon_code = "01d"  # Default icon


class UI:
    """
    A container for all LVGL UI objects and state variables
    to avoid excessive global variables.
    """
    main_screen = None
    # Header
    date_label = None
    time_label = None
    wifi_icon = None
    # Status
    desc_label = None
    weather_icon = None
    # Weather Tiles
    temp_value_label = None
    hum_value_label = None
    wind_value_label = None
    press_value_label = None
    # Cache for icon paths to avoid unnecessary UI updates
    _current_weather_icon = ""
    _current_wifi_icon = ""


ui = UI()


def set_weather_data(data, icon_code=None):
    """
    Updates the global weather data from an external source (e.g., weather module).

    Args:
        data (tuple): A tuple containing weather information.
        icon_code (str, optional): The icon code for the current weather. Defaults to None.
    """
    global weather_data, weather_icon_code
    weather_data = data
    if icon_code:
        weather_icon_code = icon_code


def _create_card(parent, x, y, width, height):
    """
    Helper function to create a styled card object.

    Args:
        parent (lv.obj): The parent object for the card.
        x (int): X position.
        y (int): Y position.
        width (int): Card width.
        height (int): Card height.

    Returns:
        lv.obj: The created card object.
    """
    card = lv.obj(parent)
    card.set_size(width, height)
    card.set_pos(x, y)
    card.set_style_bg_color(lv.color_hex(COLOR_CARD_BG), 0)
    card.set_style_radius(10, 0)
    card.set_style_border_width(0, 0)
    card.set_style_shadow_width(10, 0)
    card.set_style_shadow_opa(80, 0)
    card.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    card.set_style_pad_all(0, 0)
    return card


def _create_header(parent):
    """Creates the header section with Wi-Fi icon, date, and time."""
    header_card = _create_card(parent, 5, 5, 230, 60)

    ui.wifi_icon = lv.image(header_card)
    ui.wifi_icon.set_src(f"S:/icons/wifi_off.bin")
    ui.wifi_icon.align(lv.ALIGN.LEFT_MID, 5, 0)

    time_container = lv.obj(header_card)
    time_container.set_size(170, 58)
    time_container.align(lv.ALIGN.RIGHT_MID, 0, 0)
    time_container.set_style_bg_opa(0, 0)
    time_container.set_style_border_width(0, 0)
    time_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

    ui.date_label = lv.label(time_container)
    ui.date_label.set_text("--.--.----")
    ui.date_label.set_style_text_color(lv.color_hex(COLOR_TEXT_SECONDARY), 0)
    ui.date_label.center()
    ui.date_label.set_y(-12)

    ui.time_label = lv.label(time_container)
    ui.time_label.set_text("--:--:--")
    ui.time_label.set_style_text_color(lv.color_hex(COLOR_PRIMARY), 0)
    ui.time_label.center()
    ui.time_label.set_y(12)


def _create_status_section(parent):
    """Creates the status section with weather description and icon."""
    status_card = _create_card(parent, 5, 70, 230, 80)

    ui.weather_icon = lv.image(status_card)
    ui.weather_icon.set_src(f"S:/icons/{weather_icon_code}.bin")
    ui.weather_icon.align(lv.ALIGN.RIGHT_MID, -10, 0)

    ui.desc_label = lv.label(status_card)
    ui.desc_label.set_text("Loading...")
    ui.desc_label.set_style_text_color(lv.color_hex(COLOR_TEXT_SECONDARY), 0)
    ui.desc_label.align(lv.ALIGN.LEFT_MID, 10, 0)
    ui.desc_label.set_long_mode(ui.desc_label.LONG_MODE.WRAP)
    ui.desc_label.set_width(140)


def _create_weather_tile(parent, x, y, title, initial_value, color):
    """
    Creates a single weather data tile.

    Args:
        parent (lv.obj): The parent object for the tile.
        x (int): X position.
        y (int): Y position.
        title (str): The title text for the tile (e.g., "Temp").
        initial_value (str): The initial value to display (e.g., "--°C").
        color (int): The LVGL color hex value for the title.

    Returns:
        lv.label: The LVGL label object for the value, allowing it to be updated.
    """
    card = _create_card(parent, x, y, 110, 80)

    title_label = lv.label(card)
    title_label.set_text(title)
    title_label.set_style_text_color(lv.color_hex(color), 0)
    title_label.align(lv.ALIGN.TOP_MID, 0, 8)

    value_label = lv.label(card)
    value_label.set_text(initial_value)
    value_label.set_style_text_color(lv.color_hex(COLOR_TEXT_PRIMARY), 0)
    value_label.align(lv.ALIGN.TOP_MID, 0, 40)
    return value_label


def create_ui():
    """
    Creates the complete user interface, including all widgets.
    This function should be called once at startup.
    """
    ui.main_screen = lv.obj()
    ui.main_screen.set_style_bg_color(lv.color_hex(COLOR_BG), 0)
    lv.screen_load(ui.main_screen)

    _create_header(ui.main_screen)
    _create_status_section(ui.main_screen)

    # --- Weather Tiles ---
    ui.temp_value_label = _create_weather_tile(ui.main_screen, 5, 155, "Temp", "--°C", COLOR_ACCENT)
    ui.hum_value_label = _create_weather_tile(ui.main_screen, 125, 155, "Humid", "--%", COLOR_PRIMARY)
    ui.wind_value_label = _create_weather_tile(ui.main_screen, 5, 240, "Wind", "--m/s", COLOR_ACCENT)
    ui.press_value_label = _create_weather_tile(ui.main_screen, 125, 240, "Bar", "---hPa", COLOR_SECONDARY)

    print("✓ UI created")
    # Perform an initial update to show something immediately
    update_time_display()
    update_weather_display()


def update_time_display():
    """Updates the date and time labels on the display."""
    if ui.date_label and ui.time_label:
        now = time.localtime()
        ui.date_label.set_text(f"{now[2]:02d}.{now[1]:02d}.{now[0]:04d}")
        ui.time_label.set_text(f"{now[3]:02d}:{now[4]:02d}:{now[5]:02d}")


def update_weather_display():
    """
    Updates all weather-related data and icons on the display.
    This function only changes widgets if their values have changed.
    """
    if not ui.main_screen:
        return

    try:
        # Check if weather data is valid (not all None)
        data_is_valid = weather_data and all(val is not None for val in weather_data)

        # Update Weather Icon
        # Show a default "mist" icon (50d) if data is not valid
        new_weather_icon = weather_icon_code if data_is_valid else "50d"
        if new_weather_icon != ui._current_weather_icon:
            path = f"S:/icons/{new_weather_icon}.bin"
            ui.weather_icon.set_src(path)
            ui._current_weather_icon = new_weather_icon
            print(f"✓ Weather icon updated to: {new_weather_icon}")

        # Update Wi-Fi Icon
        # The weather data validity is a good proxy for Wi-Fi/API health.
        new_wifi_status = "on" if data_is_valid else "off"
        if new_wifi_status != ui._current_wifi_icon:
            path = f"S:/icons/wifi_{new_wifi_status}.bin"
            ui.wifi_icon.set_src(path)
            ui._current_wifi_icon = new_wifi_status
            print(f"✓ Wi-Fi icon updated to: {new_wifi_status}")

        # Update Text Labels
        if data_is_valid:
            ui.temp_value_label.set_text(f"{weather_data[0]:.1f}°C")
            ui.desc_label.set_text(str(weather_data[5]))
            ui.press_value_label.set_text(f"{weather_data[1]}hPa")
            ui.hum_value_label.set_text(f"{weather_data[2]:.0f}%")
            ui.wind_value_label.set_text(f"{weather_data[3]:.1f}m/s")
        else:
            ui.desc_label.set_text("No data")
            ui.temp_value_label.set_text("--°C")
            ui.press_value_label.set_text("---hPa")
            ui.hum_value_label.set_text("--%")
            ui.wind_value_label.set_text("--m/s")

    except Exception as e:
        print(f"ERROR in update_weather_display: {e}")
        sys.print_exception(e)


def display_handler(timer=None):
    """
    Timer callback for all display updates. Called periodically.

    Args:
        timer (object, optional): The timer object that triggered the call. Not used.
    """
    try:
        gc.collect()
        update_time_display()
        update_weather_display()
        # lv.task_handler() is called by the main loop or another timer if needed
        lv.refr_now(None) # Force immediate refresh of the display
    except Exception as e:
        print(f"ERROR in display_handler: {e}")
        sys.print_exception(e)