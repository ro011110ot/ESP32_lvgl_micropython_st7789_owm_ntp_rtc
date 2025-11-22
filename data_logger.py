"""
This module handles logging of sensor and weather data to a CSV file.

It ensures the log directory exists and writes data with a timestamp and a header.
"""

# Standard Library
import os
import utime

# --- CONSTANTS ---
LOG_DIR = "/temp_history"
LOG_FILE = LOG_DIR + "/sensor_weather_log.csv"
# Define the header for the CSV file
HEADER = "timestamp,temp_dht,humi_dht,temp_owm,pressure_owm,humi_owm,windspeed_owm,winddeg_owm,weather_desc"


def ensure_log_directory():
    """Ensures the log directory exists on the filesystem."""
    try:
        os.mkdir(LOG_DIR)
    except OSError as e:
        # Error 17 (EEXIST) is normal if the directory already exists.
        if e.args[0] != 17:
            print("Error creating log directory:", e)


def log_data(dht_data, owm_data):
    """
    Writes combined sensor (DHT) and weather (OWM) data to the CSV file.

    Args:
        dht_data (tuple): A tuple containing (temperature, humidity) from the DHT sensor.
        owm_data (tuple): A tuple containing weather data from the OWM API.
    """
    # 1. Ensure directory exists
    ensure_log_directory()

    # 2. Prepare timestamp in a spreadsheet-friendly format
    current_time = utime.localtime()
    # Format: YYYY-MM-DD HH:MM:SS
    timestamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        current_time[0],
        current_time[1],
        current_time[2],
        current_time[3],
        current_time[4],
        current_time[5],
    )

    # 3. Combine all data into a single tuple for the CSV row
    data_row = (timestamp,) + dht_data + owm_data

    # 4. Create the comma-separated string line
    # Replace None with empty string for cleaner CSV output
    data_line = ",".join(str(x) if x is not None else '' for x in data_row)

    # 5. Write to the file, adding a header if the file is new
    try:
        # Check if file exists to determine if the header needs to be written
        write_header = False
        try:
            os.stat(LOG_FILE)
        except OSError:
            write_header = True

        with open(LOG_FILE, "a") as f:
            if write_header:
                f.write(HEADER + "\n")
            f.write(data_line + "\n")

        # print("Data successfully logged to CSV:", data_line)

    except Exception as e:
        print("Error writing to log file:", e)