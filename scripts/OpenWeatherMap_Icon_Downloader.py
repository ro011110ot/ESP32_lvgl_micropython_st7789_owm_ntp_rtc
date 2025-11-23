#!/usr/bin/env python3
"""
OpenWeatherMap Icon Downloader
Lädt alle Wetter-Icons von OpenWeatherMap herunter und bereitet sie für ESP32 vor.
"""

from pathlib import Path

import requests
from PIL import Image

# Basis-URL für OpenWeatherMap Icons
BASE_URL = "https://openweathermap.org/img/wn/"

# Alle verfügbaren Icon-Codes (Tag und Nacht Versionen)
# Format: Code + 'd' für Tag, 'n' für Nacht
ICON_CODES = [
    "01",  # Clear sky
    "02",  # Few clouds
    "03",  # Scattered clouds
    "04",  # Broken clouds
    "09",  # Shower rain
    "10",  # Rain
    "11",  # Thunderstorm
    "13",  # Snow
    "50",  # Mist/Fog
]

# Icons mit OWM-Code als Dateiname (direkt nutzbar!)
# Keine Umbenennung nötig - Icons bleiben 01d.png, 10n.png, etc.


def download_icon(icon_code, output_dir, size="@2x"):
    """
    Lädt ein einzelnes Icon herunter.

    Args:
        icon_code: Icon-Code (z.B. "01d", "10n")
        output_dir: Ausgabeverzeichnis
        size: "@2x" für 100x100px oder "@4x" für 200x200px
    """
    url = f"{BASE_URL}{icon_code}{size}.png"
    output_path = output_dir / f"{icon_code}.png"  # Originaler OWM-Code als Dateiname!

    try:
        print(f"Lade {icon_code}.png ...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Bild speichern
        with open(output_path, "wb") as f:
            f.write(response.content)

        print(f"  ✓ Gespeichert: {output_path}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Fehler beim Herunterladen von {icon_code}: {e}")
        return False


def resize_for_esp32(input_dir, output_dir, target_size=(48, 48)):
    """
    Skaliert alle Icons auf ESP32-gerechte Größe (48x48 oder 32x32).

    Args:
        input_dir: Verzeichnis mit Original-Icons
        output_dir: Ausgabeverzeichnis für skalierte Icons
        target_size: Zielgröße als Tuple (width, height)
    """
    output_dir.mkdir(exist_ok=True)

    print(f"\nSkaliere Icons auf {target_size[0]}x{target_size[1]}px für ESP32...")

    for png_file in input_dir.glob("*.png"):
        try:
            img = Image.open(png_file)

            # Auf Zielgröße skalieren mit hoher Qualität
            img_resized = img.resize(target_size, Image.Resampling.LANCZOS)

            # Speichern
            output_path = output_dir / png_file.name
            img_resized.save(output_path, optimize=True)

            print(f"  ✓ {png_file.name} → {output_path}")

        except Exception as e:
            print(f"  ✗ Fehler bei {png_file.name}: {e}")


def create_mapping_file(output_dir):
    """
    Erstellt eine Python-Datei mit dem Icon-Mapping für MicroPython.
    """
    mapping_path = output_dir / "icon_mapping.py"

    with open(mapping_path, "w", encoding="utf-8") as f:
        f.write('"""\n')
        f.write("OpenWeatherMap Icon Mapping für ESP32\n")
        f.write(
            "Die Dateien sind direkt nach OWM-Codes benannt: 01d.png, 10n.png, etc.\n"
        )
        f.write('"""\n\n')
        f.write("# Verwendung im Code:\n")
        f.write('# icon_path = f"S:/icons/{owm_icon_code}.png"\n')
        f.write('# Beispiel: "10d" -> "S:/icons/10d.png"\n\n')
        f.write("# Alle verfügbaren Icon-Codes:\n")
        f.write("AVAILABLE_ICONS = [\n")

        for code in ICON_CODES:
            f.write(f'    "{code}d", "{code}n",  # Tag/Nacht\n')

        f.write("]\n")

    print(f"\n✓ Mapping-Datei erstellt: {mapping_path}")


def main():
    """
    Hauptfunktion - lädt alle Icons herunter und bereitet sie vor.
    """
    print("=" * 60)
    print("OpenWeatherMap Icon Downloader für ESP32")
    print("=" * 60)

    # Verzeichnisse erstellen
    base_dir = Path("icons_png")
    original_dir = base_dir / "original"
    esp32_48_dir = base_dir / "esp32_48x48"
    esp32_32_dir = base_dir / "esp32_32x32"

    original_dir.mkdir(parents=True, exist_ok=True)

    # Schritt 1: Icons herunterladen
    print("\n[1/4] Lade Icons von OpenWeatherMap...")
    success_count = 0

    for code in ICON_CODES:
        # Tag-Version
        if download_icon(f"{code}d", original_dir):
            success_count += 1

        # Nacht-Version
        if download_icon(f"{code}n", original_dir):
            success_count += 1

    print(f"\n✓ {success_count} Icons erfolgreich heruntergeladen")

    # Schritt 2: Für ESP32 skalieren (48x48)
    print("\n[2/4] Skaliere Icons auf 48x48px...")
    resize_for_esp32(original_dir, esp32_48_dir, (48, 48))

    # Schritt 3: Alternative Größe (32x32)
    print("\n[3/4] Skaliere Icons auf 32x32px...")
    resize_for_esp32(original_dir, esp32_32_dir, (32, 32))

    # Schritt 4: Mapping-Datei erstellen
    print("\n[4/4] Erstelle Icon-Mapping...")
    create_mapping_file(base_dir)

    # Zusammenfassung
    print("\n" + "=" * 60)
    print("✓ FERTIG!")
    print("=" * 60)
    print(f"\nVerzeichnisse:")
    print(f"  Original (100x100):  {original_dir}")
    print(f"  ESP32 (48x48):       {esp32_48_dir}")
    print(f"  ESP32 (32x32):       {esp32_32_dir}")
    print(f"\nNächste Schritte:")
    print(f"  1. Icons aus esp32_48x48/ auf ESP32 hochladen")
    print(f"  2. Icons direkt nach OWM-Code referenzieren")
    print(f"  3. In deinem Code: icon_path = f'S:/icons/{{owm_code}}.png'")
    print("\nBeispiel mit ampy:")
    print(f"  ampy --port /dev/ttyUSB0 put {esp32_48_dir}/01d.png /icons/01d.png")
    print(f"\nOder alle auf einmal (Bash):")
    print(
        f"  cd {esp32_48_dir} && for f in *.png; do ampy --port /dev/ttyUSB0 put $f /icons/$f; done"
    )
    print("=" * 60)


if __name__ == "__main__":
    # Prüfen ob PIL installiert ist
    try:
        import PIL
    except ImportError:
        print("FEHLER: Pillow (PIL) ist nicht installiert!")
        print("Installation: pip install Pillow requests")
        exit(1)

    main()
