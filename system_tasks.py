"""
This module runs periodic, non-critical system maintenance tasks.

It uses a non-blocking, "virtual timer" approach by checking `utime.ticks_ms()`
in the main loop. This is suitable for tasks that are not time-critical,
such as checking the Wi-Fi connection and re-syncing the NTP time.
"""

# Standard Library
import utime

# Local Application
import ntp
import wifi
from secrets import secrets

# --- Configuration for Virtual Timers ---
WLAN_CHECK_INTERVAL_MS = 30000  # 30 seconds
NTP_SYNC_INTERVAL_MS = 6 * 60 * 60 * 1000  # 6 hours

# --- State Variables for Virtual Timers ---
wlan_check_last_ms = 0
ntp_sync_last_ms = 0


def run_system_tasks():
    """
    Runs periodic system maintenance tasks using software timers.

    This function must be called continuously within the main application loop.
    """
    global wlan_check_last_ms
    global ntp_sync_last_ms

    current_ms = utime.ticks_ms()

    # --- Task 1: Periodic WLAN Check ---
    if utime.ticks_diff(current_ms, wlan_check_last_ms) >= WLAN_CHECK_INTERVAL_MS:
        if not wifi.is_connected():
            print("System Task: WiFi connection lost. Attempting reconnection...")
            # Re-run the full connection function to handle all cases
            wifi.connect_wifi()

        wlan_check_last_ms = current_ms

    # --- Task 2: Periodic NTP Synchronization ---
    if utime.ticks_diff(current_ms, ntp_sync_last_ms) >= NTP_SYNC_INTERVAL_MS:
        if wifi.is_connected():
            print("System Task: Performing 6-hour NTP sync...")
            ntp.set_rtc_from_ntp()
        else:
            print("System Task: Skipping NTP sync, WLAN is disconnected.")
        # Update the timestamp regardless of success to avoid rapid retries
        ntp_sync_last_ms = current_ms
