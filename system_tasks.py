"""
This module runs periodic, non-critical system maintenance tasks.

It uses a non-blocking, "virtual timer" approach by checking `utime.ticks_ms()`
in the main loop. This is suitable for tasks that are not time-critical,
such as checking the Wi-Fi connection and re-syncing the NTP time.
"""

import utime

import ntp
import wifi

# --- Configuration for Virtual Timers ---
WLAN_CHECK_INTERVAL_MS = 30000  # 30 seconds
NTP_SYNC_INTERVAL_MS = 6 * 60 * 60 * 1000  # 6 hours (6 hours * 60 min/hr * 60 sec/min * 1000 ms/sec)

# --- State Variables for Virtual Timers ---
wlan_check_last_ms = 0
ntp_sync_last_ms = 0


def run_system_tasks():
    """
    Executes periodic system maintenance tasks using a non-blocking software timer approach.

    This function should be called frequently within the main application loop.
    It checks if predefined intervals have passed for tasks like Wi-Fi monitoring
    and NTP synchronization, and executes them if necessary.
    """
    global wlan_check_last_ms
    global ntp_sync_last_ms

    current_ms = utime.ticks_ms()

    # --- Task 1: Periodic WLAN Check ---
    # Checks if the Wi-Fi connection is still active and attempts to reconnect if lost.
    if utime.ticks_diff(current_ms, wlan_check_last_ms) >= WLAN_CHECK_INTERVAL_MS:
        if not wifi.is_connected():
            print("System Task: WiFi connection lost. Attempting reconnection...")
            # Re-run the full connection function to handle all cases (e.g., multiple SSIDs)
            wifi.connect_wifi()
        wlan_check_last_ms = current_ms

    # --- Task 2: Periodic NTP Synchronization ---
    # Re-synchronizes the device's RTC with an NTP server at a longer interval.
    if utime.ticks_diff(current_ms, ntp_sync_last_ms) >= NTP_SYNC_INTERVAL_MS:
        if wifi.is_connected():
            print("System Task: Performing 6-hour NTP sync...")
            try:
                ntp.set_rtc_from_ntp()
            except Exception as e:
                print(f"System Task: NTP sync failed: {e}")
        else:
            print("System Task: Skipping NTP sync, WLAN is disconnected.")
        # Update the timestamp regardless of success to avoid rapid retries on failure
        ntp_sync_last_ms = current_ms