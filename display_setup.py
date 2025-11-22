# Datei: display_setup.py (Neu)

import lcd_bus
import machine
import st7789
import lvgl as lv
import gc

# --- PIN-DEFINITIONEN ---
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


def init_display_driver():
    """Initialisiert den SPI-Bus und den ST7789-Treiber für LVGL."""
    if not lv.is_initialized():
        lv.init()

    gc.collect()

    try:
        # S1: Hardware SPI-Bus erstellen
        spi_bus = machine.SPI.Bus(host=_HOST, mosi=_MOSI, miso=_MISO, sck=_SCK)

        # S2: Logischen Display-Bus erstellen
        display_bus = lcd_bus.SPIBus(
            spi_bus=spi_bus, dc=_DC, cs=_LCD_CS, freq=_LCD_FREQ
        )

        # S3: ST7789 Treiber instanziieren
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

        # S4: Display initialisieren und rotieren
        display.init()
        display.set_rotation(2)  # 180° Drehung
        display.set_backlight(100)

        print("LVGL Display-Treiber initialisiert.")
        return True

    except Exception as e:
        print(f"FATAL: Display-Initialisierung fehlgeschlagen: {e}")
        return False
