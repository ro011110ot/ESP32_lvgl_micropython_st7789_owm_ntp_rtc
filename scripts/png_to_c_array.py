#!/usr/bin/env python3
"""
Konvertiert PNG-Icons zu LVGL C-Arrays (Python Format)
Diese können direkt in MicroPython geladen werden
"""

from PIL import Image


def png_to_lvgl_array(png_path, output_path, var_name):
    """
    Konvertiert PNG zu LVGL RGB565 C-Array im Python-Format
    """
    # PNG laden
    img = Image.open(png_path)
    img = img.convert("RGB")  # Zu RGB konvertieren

    width, height = img.size

    print(f"Konvertiere {png_path}...")
    print(f"  Größe: {width}x{height}")

    # RGB565 Daten sammeln
    rgb565_data = []

    for y in range(height):
        for x in range(width):
            r, g, b = img.getpixel((x, y))

            # RGB888 zu RGB565 konvertieren
            r5 = (r >> 3) & 0x1F  # 5 bits
            g6 = (g >> 2) & 0x3F  # 6 bits
            b5 = (b >> 3) & 0x1F  # 5 bits

            # RGB565 zusammensetzen (Big Endian)
            rgb565 = (r5 << 11) | (g6 << 5) | b5

            # Als 2 Bytes speichern
            byte_high = (rgb565 >> 8) & 0xFF
            byte_low = rgb565 & 0xFF

            rgb565_data.append(byte_high)
            rgb565_data.append(byte_low)

    # Python-Datei schreiben
    with open(output_path, "w") as f:
        f.write(f'"""\n')
        f.write(f"LVGL Image: {var_name}\n")
        f.write(f"Generated from: {png_path}\n")
        f.write(f"Size: {width}x{height}\n")
        f.write(f"Format: RGB565\n")
        f.write(f'"""\n\n')

        f.write(f"# Image data\n")
        f.write(f"{var_name}_width = {width}\n")
        f.write(f"{var_name}_height = {height}\n")
        f.write(f"{var_name}_data = bytes([\n")

        # Daten in Zeilen von 16 Bytes schreiben
        for i in range(0, len(rgb565_data), 16):
            chunk = rgb565_data[i : i + 16]
            hex_str = ", ".join(f"0x{b:02X}" for b in chunk)
            f.write(f"    {hex_str},\n")

        f.write(f"])\n")

    print(f"  ✓ Gespeichert: {output_path}")
    print(f"  Größe: {len(rgb565_data)} bytes")


def convert_all_weather_icons():
    """
    Konvertiert alle Wetter-Icons
    """
    icons = [
        ("01d", "clear_day"),
        ("01n", "clear_night"),
        ("02d", "few_clouds_day"),
        ("02n", "few_clouds_night"),
        ("03d", "scattered_clouds"),
        ("03n", "scattered_clouds_night"),
        ("04d", "broken_clouds"),
        ("04n", "broken_clouds_night"),
        ("09d", "shower_rain"),
        ("09n", "shower_rain_night"),
        ("10d", "rain_day"),
        ("10n", "rain_night"),
        ("11d", "thunderstorm"),
        ("11n", "thunderstorm_night"),
        ("13d", "snow"),
        ("13n", "snow_night"),
        ("50d", "mist"),
        ("50n", "mist_night"),
    ]

    # Auch WLAN-Icons
    icons.extend(
        [
            ("wifi_on", "wifi_on"),
            ("wifi_off", "wifi_off"),
        ]
    )

    print("=" * 60)
    print("PNG zu LVGL C-Array Konverter")
    print("=" * 60)

    for code, var_name in icons:
        png_path = f"icons_png/{code}.png"
        output_path = f"icon_data_{code}.py"

        try:
            png_to_lvgl_array(png_path, output_path, var_name)
        except FileNotFoundError:
            print(f"  ⚠ Datei nicht gefunden: {png_path}")
        except Exception as e:
            print(f"  ✗ Fehler: {e}")

    print("\n" + "=" * 60)
    print("✓ Konvertierung abgeschlossen")
    print("=" * 60)
    print("\nNächste Schritte:")
    print("  1. Alle icon_data_*.py Dateien auf ESP32 hochladen")
    print("  2. Icons im Code laden mit:")
    print(
        "     from icon_data_01d import clear_day_width, clear_day_height, clear_day_data"
    )
    print("     img_dsc = lv.img_dsc_t()")
    print("     img_dsc.data = clear_day_data")
    print("     img_dsc.header.w = clear_day_width")
    print("     img_dsc.header.h = clear_day_height")
    print("     img_dsc.header.cf = lv.COLOR_FORMAT.RGB565")
    print("     img.set_src(img_dsc)")


if __name__ == "__main__":
    convert_all_weather_icons()
