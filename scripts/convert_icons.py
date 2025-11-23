import os
import struct

from PIL import Image

# --- KONFIGURATION ---
INPUT_DIR = "icons_png"
OUTPUT_DIR = "icons"


def convert_to_rgb565(r, g, b):
    """Konvertiert 8-Bit RGB in 16-Bit RGB565 (Little Endian für ESP32)."""
    # 5 Bits Rot, 6 Bits Grün, 5 Bits Blau
    r5 = (r >> 3) & 0x1F
    g6 = (g >> 2) & 0x3F
    b5 = (b >> 3) & 0x1F

    # Zusammenfügen: RRRRRGGGGGGBBBBB
    word = (r5 << 11) | (g6 << 5) | b5

    # WICHTIG: ESP32 ist Little Endian, LVGL Treiber erwarten meist Little Endian.
    # Wenn die Farben falsch sind (Blau/Rot vertauscht), hier auf '>H' ändern.
    # Aber '<H' ist der Standard für 'Binary' Format in LVGL.
    return struct.pack("<H", word)


def process_image(input_path, output_path):
    print(f"Verarbeite: {os.path.basename(input_path)}...")
    try:
        img = Image.open(input_path).convert("RGB")
        width, height = img.size

        with open(output_path, "wb") as f_out:
            # --- LVGL HEADER ERSTELLEN (WICHTIG!) ---
            # LVGL v8/v9 Binary Image Header (vinfmt_bin)
            # Byte 0: Magic (0x19 für LV_IMAGE_HEADER_MAGIC)
            # Byte 1: Color Format (4 für LV_IMG_CF_TRUE_COLOR / RGB565)
            # Byte 2-3: Flags (0)
            # Byte 4-5: Breite (Little Endian)
            # Byte 6-7: Höhe (Little Endian)
            # Byte 8-9: Stride (Breite * 2 bytes, Little Endian)
            # Byte 10-11: Reserved (0)

            magic = 0x19
            cf = 4  # LV_IMG_CF_TRUE_COLOR (funktioniert meistens für RGB565)
            flags = 0
            stride = width * 2

            # Header packen (Little Endian)
            header = struct.pack("<BBHHHHH", magic, cf, flags, width, height, stride, 0)
            f_out.write(header)

            # --- PIXEL DATEN ---
            for y in range(height):
                for x in range(width):
                    r, g, b = img.getpixel((x, y))

                    # Schwarz zu Weiß Hack (optional)
                    if r == 0 and g == 0 and b == 0:
                        r, g, b = 255, 255, 255

                    pixel_bytes = convert_to_rgb565(r, g, b)
                    f_out.write(pixel_bytes)

        print(f"-> Erfolg: {output_path} ({width}x{height} Pixel + Header)")

    except Exception as e:
        print(f"FEHLER bei {input_path}: {e}")


def main():
    if not os.path.exists(INPUT_DIR):
        print(f"Erstelle '{INPUT_DIR}'...")
        os.makedirs(INPUT_DIR)
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith((".png", ".jpg"))]
    if not files:
        print("Keine Bilder gefunden.")
        return

    for filename in files:
        input_path = os.path.join(INPUT_DIR, filename)
        output_filename = os.path.splitext(filename)[0] + ".bin"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        process_image(input_path, output_path)

    print("\nFertig! Kopiere den Ordner 'icons' auf den ESP32.")


if __name__ == "__main__":
    main()
