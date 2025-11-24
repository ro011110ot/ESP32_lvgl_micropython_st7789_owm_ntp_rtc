#!/usr/bin/env python3
"""
OpenWeatherMap Icon Downloader

This script downloads OpenWeatherMap weather icons, resizes them to suitable
dimensions for ESP32 displays, and prepares them for further conversion to
LVGL's binary format.
"""

from pathlib import Path

import requests
from PIL import Image

# Base URL for OpenWeatherMap Icons
BASE_URL = "https://openweathermap.org/img/wn/"

# All available icon codes (day and night versions) from OpenWeatherMap
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

# Additional icons not directly from OWM weather codes but used in the project
ADDITIONAL_ICONS = [
    "wifi_on",
    "wifi_off",
]


def download_icon(icon_name: str, output_dir: Path, size: str = "@2x") -> bool:
    """
    Downloads a single icon from OpenWeatherMap.

    Args:
        icon_name (str): The icon code (e.g., "01d", "10n", "wifi_on").
        output_dir (Path): The directory where the icon will be saved.
        size (str): The desired icon size suffix (e.g., "@2x" for 100x100px, "@4x" for 200x200px).
                    Note: This only applies to OWM icons.

    Returns:
        bool: True if the download was successful, False otherwise.
    """
    # Construct URL for OWM icons. Additional icons are assumed to be named directly.
    if icon_name.startswith(("0", "1", "5")): # Heuristic for OWM icons
        url = f"{BASE_URL}{icon_name}{size}.png"
    else: # Assume additional icons are already full names like 'wifi_on.png'
        # For simplicity, we assume additional icons are not part of the OWM base URL
        # and would need to be fetched from a different source or copied manually.
        # This script focuses on OWM icons, so we'll skip direct download for these.
        print(f"Skipping download for non-OWM icon: {icon_name}. Please provide manually if needed.")
        return False


    output_path = output_dir / f"{icon_name}.png"
    try:
        print(f"Downloading {icon_name}.png ...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)

        # Save the image
        with open(output_path, "wb") as f:
            f.write(response.content)

        print(f"  ✓ Saved: {output_path}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error downloading {icon_name}: {e}")
        return False
    except Exception as e:
        print(f"  ✗ An unexpected error occurred for {icon_name}: {e}")
        return False


def resize_icons(input_dir: Path, output_dir: Path, target_size: tuple = (48, 48)) -> None:
    """
    Resizes all PNG icons in the input directory to a target size.

    Args:
        input_dir (Path): Directory containing the original icons.
        output_dir (Path): Directory to save the resized icons.
        target_size (tuple): Target size as (width, height) in pixels.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nResizing icons to {target_size[0]}x{target_size[1]}px for ESP32...")

    for png_file in input_dir.glob("*.png"):
        try:
            img = Image.open(png_file)

            # Resize to target size with high quality resampling
            img_resized = img.resize(target_size, Image.Resampling.LANCZOS)

            # Save the resized image
            output_path = output_dir / png_file.name
            img_resized.save(output_path, optimize=True)

            print(f"  ✓ {png_file.name} → {output_path}")

        except Exception as e:
            print(f"  ✗ Error resizing {png_file.name}: {e}")


def main() -> None:
    """
    Main function to orchestrate the icon downloading and preparation process.
    """
    print("=" * 60)
    print("OpenWeatherMap Icon Downloader for ESP32")
    print("=" * 60)

    # Define directories
    base_output_dir = Path("icons_png")
    original_size_dir = base_output_dir / "original"
    esp32_target_dir = base_output_dir / "48x48" # Renamed to be more generic for final output for LVGL

    original_size_dir.mkdir(parents=True, exist_ok=True) # Ensure original directory exists

    # Step 1: Download Icons
    print("\n[1/2] Downloading icons from OpenWeatherMap...")
    downloaded_count = 0

    all_icon_names = []
    for code in ICON_CODES:
        all_icon_names.append(f"{code}d") # Day version
        all_icon_names.append(f"{code}n") # Night version
    # Adding additional icons to the list for processing
    all_icon_names.extend(ADDITIONAL_ICONS)


    for icon_name in all_icon_names:
        if download_icon(icon_name, original_size_dir):
            downloaded_count += 1
        elif icon_name in ADDITIONAL_ICONS:
             # Create dummy files for additional icons if not downloaded, for resizing later
            dummy_path = original_size_dir / f"{icon_name}.png"
            if not dummy_path.exists():
                print(f"  Creating dummy PNG for {icon_name}. Please replace with actual icon if needed.")
                # Create a simple white square as a placeholder
                Image.new('RGB', (100, 100), color = 'white').save(dummy_path)
                downloaded_count += 1 # Count dummy as processed

    print(f"\n✓ {downloaded_count} icons processed (downloaded or dummy created).")

    # Step 2: Resize Icons for ESP32
    print(f"\n[2/2] Resizing icons to 48x48px and saving to '{esp32_target_dir}'...")
    resize_icons(original_size_dir, esp32_target_dir, target_size=(48, 48))

    # Summary
    print("\n" + "=" * 60)
    print("✓ Icon Preparation Complete!")
    print("=" * 60)
    print(f"\nYour icons are prepared in the '{esp32_target_dir}' directory.")
    print("\nNext Steps:")
    print(f"  1. Review '{esp32_target_dir}' for your ready-to-convert PNG icons.")
    print(f"  2. Run 'convert_icons.py' (located in the same 'scripts' folder).")
    print(f"     It will convert these PNGs into LVGL-compatible '.bin' files.")
    print(f"  3. Copy the resulting '.bin' files from the 'icons' folder to your ESP32's '/icons' directory.")
    print("=" * 60)


if __name__ == "__main__":
    # Check if Pillow (PIL) is installed
    try:
        import PIL
    except ImportError:
        print("ERROR: Pillow (PIL) is not installed!")
        print("Please install it using: pip install Pillow requests")
        exit(1)

    main()