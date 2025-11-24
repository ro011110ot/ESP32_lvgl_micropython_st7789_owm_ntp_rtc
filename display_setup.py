"""
display_setup.py - Display Driver Initialization

This module handles the low-level initialization of the ST7789 display
and the SPI bus required for LVGL.
"""

import gc

import lcd_bus
import lvgl as lv
import machine
import st7789

# --- Pin Definitions ---
# The display is 240x320, but we rotate it by 180 degrees (set_rotation(2)),
# so the logical width and height are swapped for portrait mode.
_WIDTH = 240
_HEIGHT = 320

# Control Pins
_BL = 17      # Backlight control
_RST = 22     # Reset
_DC = 21      # Data/Command

# SPI Bus Pins (VSPI)
_MOSI = 23
_MISO = 19    # Not strictly needed for display-only, but good practice
_SCK = 18
_HOST = 2     # Using VSPI host

# Display-specific SPI settings
_LCD_CS = 5
_LCD_FREQ = 40000000  # 40 MHz

# Pin states
BL_STATE_HIGH = st7789.STATE_HIGH
RESET_STATE_LOW = st7789.STATE_LOW


def init_display_driver() -> bool:
    """
    Initializes the SPI bus and the ST7789 driver for LVGL.

    This function sets up the physical SPI connection, configures the
    display driver with the correct dimensions and pin settings, and
    initializes the display for use.

    Returns:
        bool: True if initialization was successful, False otherwise.
    """
    if not lv.is_initialized():
        lv.init()

    gc.collect()

    try:
        # 1. Create the hardware SPI bus
        spi_bus = machine.SPI.Bus(host=_HOST, mosi=_MOSI, miso=_MISO, sck=_SCK)

        # 2. Create the logical display bus from the SPI bus
        display_bus = lcd_bus.SPIBus(
            spi_bus=spi_bus,
            dc=_DC,
            cs=_LCD_CS,
            freq=_LCD_FREQ
        )

        # 3. Instantiate the ST7789 driver
        display_driver = st7789.ST7789(
            data_bus=display_bus,
            display_width=_WIDTH,
            display_height=_HEIGHT,
            backlight_pin=_BL,
            reset_pin=_RST,
            reset_state=RESET_STATE_LOW,
            backlight_on_state=BL_STATE_HIGH,
            color_byte_order=st7789.BYTE_ORDER_RGB,
            rgb565_byte_swap=False,
            offset_x=0,
            offset_y=0,
        )

        # 4. Initialize, rotate, and turn on the display
        display_driver.init()
        display_driver.set_rotation(2)  # Rotate 180 degrees for portrait view
        display_driver.set_backlight(100)

        print("LVGL display driver initialized successfully.")
        return True

    except Exception as e:
        print(f"FATAL: Display initialization failed: {e}")
        import sys
        sys.print_exception(e)
        return False