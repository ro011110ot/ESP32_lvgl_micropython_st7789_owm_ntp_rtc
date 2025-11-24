"""
This script converts PNG/JPG image files into a custom binary format (.bin)
suitable for use with LVGL on ESP32 microcontrollers.

It processes images from an input directory, converts their pixels to RGB565
format, and prepends an LVGL image header to each binary file.
"""

import os
import struct

from PIL import Image

# --- CONFIGURATION ---
INPUT_DIR = "icons_png"  # Directory containing source PNG/JPG images
OUTPUT_DIR = "icons"     # Directory where converted .bin files will be saved


def convert_to_rgb565(r: int, g: int, b: int) -> bytes:
    """
    Converts 8-bit RGB color components to a 16-bit RGB565 format.

    The RGB565 format uses 5 bits for Red, 6 bits for Green, and 5 bits for Blue.
    The output is packed as a little-endian short (2 bytes) for ESP32 compatibility.

    Args:
        r (int): Red component (0-255).
        g (int): Green component (0-255).
        b (int): Blue component (0-255).

    Returns:
        bytes: Two bytes representing the RGB565 color in little-endian format.
    """
    # Extract 5 bits for Red, 6 for Green, 5 for Blue
    r5 = (r >> 3) & 0x1F
    g6 = (g >> 2) & 0x3F
    b5 = (b >> 3) & 0x1F

    # Combine into a 16-bit word: RRRRRGGGGGGBBBBB
    word = (r5 << 11) | (g6 << 5) | b5

    # IMPORTANT: ESP32 is Little Endian, and LVGL drivers typically expect Little Endian.
    # If colors appear incorrect (e.g., blue/red swapped), consider changing '<H' to '>H'.
    # However, '<H' is standard for LVGL's 'Binary' image format.
    return struct.pack("<H", word)


def process_image(input_path: str, output_path: str) -> None:
    """
    Processes a single image file, converting it to LVGL's binary format.

    Opens the image, converts it to RGB, iterates through pixels, converts
    each pixel to RGB565, and writes it to an output binary file along
    with an LVGL image header.

    Args:
        input_path (str): The full path to the input image file (e.g., PNG, JPG).
        output_path (str): The full path for the output binary file (.bin).
    """
    print(f"Processing: {os.path.basename(input_path)}...")
    try:
        img = Image.open(input_path).convert("RGB")
        width, height = img.size

        with open(output_path, "wb") as f_out:
            # --- LVGL HEADER CREATION (IMPORTANT!) ---
            # LVGL v8/v9 Binary Image Header (vinfmt_bin) structure:
            # Byte 0: Magic (0x19 for LV_IMAGE_HEADER_MAGIC)
            # Byte 1: Color Format (4 for LV_IMG_CF_TRUE_COLOR / RGB565)
            # Byte 2-3: Flags (0)
            # Byte 4-5: Width (Little Endian)
            # Byte 6-7: Height (Little Endian)
            # Byte 8-9: Stride (Width * 2 bytes, Little Endian)
            # Byte 10-11: Reserved (0)

            magic = 0x19
            cf = 4  # LV_IMG_CF_TRUE_COLOR (commonly used for RGB565)
            flags = 0
            stride = width * 2  # 2 bytes per pixel for RGB565

            # Pack header (Little Endian)
            header = struct.pack("<BBHHHHH", magic, cf, flags, width, height, stride, 0)
            f_out.write(header)

            # --- PIXEL DATA ---
            for y in range(height):
                for x in range(width):
                    r, g, b = img.getpixel((x, y))

                    # Optional: "Black to White" hack.
                    # If a pixel is pure black, convert it to white.
                    # This can be useful for displays where black might be transparent
                    # or to ensure visibility of originally black elements.
                    if r == 0 and g == 0 and b == 0:
                        r, g, b = 255, 255, 255

                    pixel_bytes = convert_to_rgb565(r, g, b)
                    f_out.write(pixel_bytes)

        print(f"-> Success: {output_path} ({width}x{height} pixels + header)")

    except Exception as e:
        print(f"ERROR processing {input_path}: {e}")


def main() -> None:
    """
    Main function to orchestrate the image conversion process.

    It checks for input and output directories, lists image files,
    and calls `process_image` for each found image.
    """
    if not os.path.exists(INPUT_DIR):
        print(f"Input directory '{INPUT_DIR}' not found.")
        print(f"Please place your PNG/JPG icons in the '{INPUT_DIR}' folder.")
        os.makedirs(INPUT_DIR, exist_ok=True) # Create it for convenience
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    if not files:
        print(f"No image files (PNG, JPG) found in '{INPUT_DIR}'.")
        return

    print(f"Found {len(files)} image(s) in '{INPUT_DIR}'. Starting conversion...")
    for filename in files:
        input_path = os.path.join(INPUT_DIR, filename)
        output_filename = os.path.splitext(filename)[0] + ".bin"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        process_image(input_path, output_path)

    print(f"\nConversion complete! Copy the '{OUTPUT_DIR}' folder to your ESP32.")


if __name__ == "__main__":
    main()