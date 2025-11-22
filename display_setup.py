# File: display_setup.py (New)

import lcd_bus
import machine
import st7789
import lvgl as lv
import gc

# --- PIN DEFINITIONS ---
_WIDTH = 240
_HEIGHT = 320
_BL = 17
_RST = 22
_DC = 21

_MOSI = 23
_MISO = 19
_SCK = 18
_HOST = 2  # VSPI

_LCD_CS = 5
_LCD_FREQ = 40000000

BL_STATE_HIGH = st7789.STATE_HIGH
RESET_STATE_LOW = st7789.STATE_LOW


def init_display_driver() -> bool:
    """Initializes the SPI bus and the ST7789 driver for LVGL."""
    if not lv.is_initialized():
        lv.init()

    gc.collect()

    try:
        # S1: Create hardware SPI bus
        spi_bus = machine.SPI.Bus(host=_HOST, mosi=_MOSI, miso=_MISO, sck=_SCK)

        # S2: Create logical display bus
        display_bus = lcd_bus.SPIBus(
            spi_bus=spi_bus, dc=_DC, cs=_LCD_CS, freq=_LCD_FREQ
        )

        # S3: Instantiate ST7789 driver
        display = st7789.ST7789(
            data_bus=display_bus,
            display_width=_WIDTH,
            display_height=_HEIGHT,
            backlight_pin=_BL,
            reset_pin=_RST,
            reset_state=RESET_STATE_LOW,
            backlight_on_state=BL_STATE_HIGH,
            color_byte_order=st7789.BYTE_ORDER_BGR,
            rgb565_byte_swap=True,
        )

        # S4: Initialize and rotate display
        display.init()
        display.set_rotation(2)  # 180° rotation
        display.set_backlight(100)

        print("LVGL display driver initialized.")
        return True

    except Exception as e:
        print(f"FATAL: Display initialization failed: {e}")
        return False
