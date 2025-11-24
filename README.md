# ESP32 LVGL Weather Station

This project transforms an ESP32 into a weather station using a ST7789 display with the LVGL graphics library. It fetches weather data from the OpenWeatherMap API, synchronizes time using NTP, and displays the information in a clean user interface with weather icons.

## Features

-   Connects to a Wi-Fi network using credentials from a `secrets.py` file.
-   Synchronizes the Real-Time Clock (RTC) with an NTP server, including CET/CEST daylight saving adjustments.
-   Fetches current weather data from OpenWeatherMap (temperature, pressure, humidity, wind, and description).
-   Displays the current date, time, and weather information, including weather icons, on a 240x320 ST7789 TFT display.
-   Uses the LVGL library for a modern and responsive user interface.
-   Modular structure for easy maintenance and extension.

## File Descriptions

-   **`main.py`**: The main entry point of the application. It initializes the display, connects to Wi-Fi, syncs NTP time, and starts the main application loop.
-   **`boot.py`**: Executed on every boot. Can be used for initial setup like enabling WebREPL or debugging.
-   **`secrets.py`**: (Not included in the repository) Stores sensitive information like Wi-Fi credentials and API keys.
-   **`wifi.py`**: Handles the Wi-Fi connection, with robust logic for retries and multiple credential support.
-   **`ntp.py`**: Manages time synchronization with an NTP server and handles local time conversion (CET/CEST).
-   **`weather.py`**: Fetches and parses weather data from the OpenWeatherMap API.
-   **`display_setup.py`**: Initializes the ST7789 display driver and the underlying SPI bus for LVGL.
-   **`display.py`**: Manages the entire LVGL user interface, including creating widgets (labels, images) and updating them with new data.
-   **`own_timers.py`**: Configures and starts hardware timers for periodic tasks like updating the display clock and fetching new weather data.
-   **`system_tasks.py`**: Runs non-critical, periodic maintenance tasks, such as checking the Wi-Fi connection, using a non-blocking approach.

## Hardware Requirements

-   ESP32 development board (with sufficient PSRAM recommended for LVGL).
-   ST7789 TFT LCD Display (240x320 resolution).
-   Breadboard and jumper wires for connections.

## Setup

1.  **Install MicroPython with LVGL & ST7789 Driver:** Flash your ESP32 with a recent version of MicroPython that includes LVGL bindings. You can find a firmware for the ESP32_GENERIC under `/firmware` or you can compile it with the [LVGL MicroPython repository](https://github.com/lvgl-micropython/lvgl_micropython).
2.  **Copy Project Files:** Upload all the `.py` files from this project to the root directory of your ESP32's filesystem.
3.  **Create `secrets.py`:** Create a file named `secrets.py` in the root directory with the following structure. You can add multiple Wi-Fi networks; the system will attempt to connect to them in order.

    ```python
    secrets = {
        "wifi_credentials": [
            {"ssid": "YOUR_WIFI_SSID", "password": "YOUR_WIFI_PASSWORD"},
            # {"ssid": "ANOTHER_SSID", "password": "ANOTHER_PASSWORD"},
        ],
        "openweather_api_key": "YOUR_OPENWEATHERMAP_API_KEY",
        "city": "YourCity",
        "country_code": "DE"  # Your two-letter country code
    }
    ```
4.  **Connect Hardware:** Connect the ST7789 display to your ESP32 according to the pin definitions in `display_setup.py`.
    -   **MOSI**: GPIO 23
    -   **MISO**: GPIO 19
    -   **SCK**: GPIO 18
    -   **CS**: GPIO 5
    -   **DC**: GPIO 21
    -   **RST**: GPIO 22
    -   **BL**: GPIO 17
5.  **Run:** The `main.py` script will run automatically on boot, starting the weather station.

## How it Works
The application starts with `main.py`, which orchestrates the setup process in several steps:
1.  **Display Initialization**: `display_setup.init_display_driver()` sets up the SPI bus and the ST7789 driver.
2.  **UI Creation**: `display.create_ui()` builds the LVGL interface, creating labels and images for time, date, and weather information.
3.  **Wi-Fi Connection**: `wifi.connect_wifi()` establishes a connection to the internet.
4.  **Time Sync**: If Wi-Fi is available, `ntp.set_rtc_from_ntp()` synchronizes the device's clock.
5.  **Timers**: `own_timers.start_timer_tasks()` starts two hardware timers:
    -   A 1-second timer that calls `display.display_handler()` to update the clock on the screen and refresh the LVGL display.
    -   A 15-minute timer that calls `weather_wrapper()` to fetch new weather data from the API.
6.  **Main Loop**: The application enters an infinite loop that continuously calls `lv.task_handler()` to process LVGL events and `run_system_tasks()` to perform background checks, ensuring the application remains responsive and stable.

## Icons and their Creation

The weather station uses custom icons for weather conditions and Wi-Fi status. These icons need to be in a specific binary format (`.bin`) for efficient rendering by LVGL on the ESP32. The `scripts` folder contains tools to help with this process.

### Process Overview

1.  **Download & Resize PNGs**: Use `scripts/OpenWeatherMap_Icon_Downloader.py` to fetch OpenWeatherMap icons and resize them to a suitable resolution (e.g., 48x48 pixels). This script will place the resulting PNGs in the `icons_png/48x48` directory. It also handles placeholder creation for `wifi_on.png` and `wifi_off.png`.
2.  **Convert PNGs to LVGL Binary Format**: Use `scripts/convert_icons.py` to convert the resized PNGs into LVGL-compatible `.bin` files. These files will be saved in the `icons` directory.
3.  **Upload to ESP32**: Copy the generated `.bin` files from the `icons` directory to the `/icons` directory on your ESP32's filesystem.

### Step-by-Step Guide

#### 1. Prepare Icons (Download & Resize)

Navigate to the `scripts` directory in your terminal and run the downloader script:

```bash
cd scripts
python3 OpenWeatherMap_Icon_Downloader.py
```

This script will:
-   Download standard OpenWeatherMap icons (e.g., `01d.png`, `10n.png`) into `icons_png/original`.
-   Resize these icons to 48x48 pixels and save them to `icons_png/48x48`.
-   Create placeholder `wifi_on.png` and `wifi_off.png` in `icons_png/original` and then resize them to `icons_png/48x48`. You can replace these placeholders with your custom Wi-Fi icons if desired.

#### 2. Convert PNGs to LVGL Binary Format

After preparing the PNGs, use the converter script:

```bash
cd scripts
python3 convert_icons.py
```

This script will:
-   Read the PNG files from the `icons_png` directory (it expects them in `icons_png/48x48` by default, but you can adjust `INPUT_DIR` in `convert_icons.py` if you used a different size).
-   Convert each PNG into a `.bin` file, adding the necessary LVGL image header.
-   Save the `.bin` files into the `icons` directory (e.g., `icons/01d.bin`, `icons/wifi_on.bin`).

#### 3. Upload Binary Icons to ESP32

Finally, upload the generated `.bin` files to your ESP32. You can use `ampy` or a similar tool. Ensure they are placed in a directory named `/icons` on your ESP32's filesystem.

Example using `ampy` (assuming your ESP32 is on `/dev/ttyUSB0`):

```bash
cd icons # Navigate to the directory containing the .bin files
ampy --port /dev/ttyUSB0 put . /icons
```

This command will upload all `.bin` files from your local `icons` directory to the `/icons` directory on your ESP32.