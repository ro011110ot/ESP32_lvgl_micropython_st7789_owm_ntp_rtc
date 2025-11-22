"""
This module logs weather data to a CSV file.

(Logging of the DHT sensor has been removed.)
"""

# Standard Library
import os
import utime
from typing import Tuple, Optional

# --- CONSTANTS ---
LOG_DIR = "/temp_history"
LOG_FILE = LOG_DIR + "/weather_log.csv"
# Header updated: Only OWM data
HEADER = "timestamp,temp_owm,pressure_owm,humi_owm,windspeed_owm,winddeg_owm,weather_desc"


def ensure_log_directory() -> None:
    """Ensures that the log directory exists on the filesystem."""
    try:
        os.mkdir(LOG_DIR)
    except OSError as e:
        # Error 17 (EEXIST) is normal if the directory already exists.
        if e.args[0] != 17:
            print("Error creating log directory:", e)


def log_data(owm_data: Tuple[Optional[float], Optional[int], Optional[int], Optional[float], Optional[int], Optional[str]]) -> None:
    """
    Writes weather data (OWM) to the CSV file.

    Args:
        owm_data (tuple): A tuple containing weather data from the OWM API.
    """
    # 1. Ensure the directory exists
    ensure_log_directory()

    # 2. Prepare the timestamp
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

    # 3. Combine data into a single row
    data_row = (timestamp,) + owm_data

    # 4. Create the comma-separated string
    data_line = ",".join(str(x) if x is not None else "" for x in data_row)

    # 5. Write to the file and add header if necessary
    try:
        write_header = False
        try:
            os.stat(LOG_FILE)
        except OSError:
            write_header = True

        with open(LOG_FILE, "a") as f:
            if write_header:
                f.write(HEADER + "\n")
            f.write(data_line + "\n")

    except Exception as e:
        print("Error writing to log file:", e)
