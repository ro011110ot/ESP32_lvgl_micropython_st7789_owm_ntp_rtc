"""
main.py - Main program for the ESP32 LVGL Weather Station.
This script coordinates the display, Wi-Fi, NTP, and sensor data.
"""

import gc
import sys
import utime

import lvgl as lv
from fs_driver import fs_register

import display
import display_setup
from ntp import set_rtc_from_ntp
from own_timers import start_timer_tasks
from system_tasks import run_system_tasks
from wifi import connect_wifi, is_connected


def main() -> None:
    """
    Main entry point and logic for the application.
    Initializes hardware, creates the UI, connects to the network,
    synchronizes time, and starts the main application loop.
    """
    print("\n" + "=" * 50)
    print("ESP32 LVGL Weather Station Started")
    print("=" * 50 + "\n")

    # ========================================
    # STEP 1: Initialize Display Hardware
    # ========================================
    print("[1/6] Initializing display hardware...")
    if not display_setup.init_display_driver():
        print("FATAL: Display hardware initialization failed!")
        print("Check SPI wiring and pin configurations.")
        return

    print("✓ Display hardware OK\n")
    gc.collect()

    # ========================================
    # STEP 2: Create LVGL UI
    # ========================================
    print("[2/6] Creating user interface...")

    # Register the file system driver for LVGL
    fs_drv = lv.fs_drv_t()
    fs_register(fs_drv, "S")

    try:
        display.create_ui()
        print("✓ UI created and initialized\n")
    except Exception as e:
        print(f"FATAL: UI creation failed: {e}")
        sys.print_exception(e)
        return

    gc.collect()

    # ========================================
    # STEP 3: Wi-Fi Connection
    # ========================================
    print("[3/6] Connecting to Wi-Fi...")
    connect_wifi()

    if not is_connected():
        print("WARNING: No Wi-Fi connection!")
        print("Displaying time only (without NTP sync).")
        print("Weather data will not be available.\n")
        # Continue without Wi-Fi to at least show the time
    else:
        print("✓ Wi-Fi connected\n")

    gc.collect()

    # ========================================
    # STEP 4: NTP Time Synchronization
    # ========================================
    if is_connected():
        print("[4/6] Synchronizing time via NTP...")
        try:
            set_rtc_from_ntp()
            print("✓ Time synchronized\n")
        except Exception as e:
            print(f"WARNING: NTP sync failed: {e}")
            print("Using system time.\n")
            sys.print_exception(e)
    else:
        print("[4/6] Skipping NTP (no Wi-Fi)\n")

    gc.collect()

    # ========================================
    # STEP 5: Start Hardware Timers
    # ========================================
    print("[5/6] Starting hardware timers...")
    try:
        start_timer_tasks()
        print("✓ Timers started:")
        print("  - Display update: every 1s")
        print("  - Weather update: every 15min\n")
    except Exception as e:
        print(f"FATAL: Timer initialization failed: {e}")
        sys.print_exception(e)
        return

    gc.collect()

    # ========================================
    # STEP 6: Main Loop
    # ========================================
    print("[6/6] Starting main loop...")
    print("=" * 50)
    print("System is running! Press CTRL+C to exit.")
    print("=" * 50 + "\n")

    try:
        while True:
            # Execute non-blocking system tasks (e.g., Wi-Fi monitoring)
            run_system_tasks()

            # LVGL's task handler is now called by a timer,
            # so we just need to keep the script alive.
            utime.sleep_ms(500)

    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("Program terminated by user (CTRL+C)")
        print("=" * 50)

    except Exception as e:
        print("\n" + "=" * 50)
        print("FATAL: Unexpected error in main loop:")
        print(f"  {e}")
        print("=" * 50)
        sys.print_exception(e)


# ========================================
# PROGRAM START
# ========================================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\n" + "=" * 50)
        print("CRITICAL ERROR ON STARTUP:")
        print(f"  {e}")
        print("=" * 50)
        sys.print_exception(e)
    finally:
        # Cleanup can be added here if needed
        print("\nProgram finished.")