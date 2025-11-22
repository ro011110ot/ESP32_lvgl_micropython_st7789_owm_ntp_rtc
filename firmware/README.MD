# LVGL (9.4.0) MicroPython (1.26.1) Binding compiled on 2025-11-22; Generic ESP32

## !!! Caution Firmware must be flashed @ 0x0 

python -m esptool --chip esp32 -p /dev/ttyUSB0 -b 460800 --before default_reset --after hard_reset write_flash --flash_mode dio --flash_size 4MB --flash_freq 40m --erase-all 0x0 ./lvgl_micropy_ESP32_GENERIC-4.bin
