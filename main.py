"""
main.py - Main program for ESP32 Weather Station with LVGL
Coordinates display, WiFi, NTP, and sensor data.
"""

# Standard Library
import utime
import gc
import lvgl as lv
import sys

# Local Application
from ntp import set_rtc_from_ntp
from own_timers import start_timer_tasks
from system_tasks import run_system_tasks
from wifi import connect_wifi, is_connected
import display_setup
import display


def main() -> None:
    """
    Main entry point and logic for the application.
    """
    print("\n" + "=" * 50)
    print("ESP32 Weather Station with LVGL started")
    print("=" * 50 + "\n")

    # ========================================
    # STEP 1: Initialize Display Hardware
    # ========================================
    print("[1/6] Initializing display hardware...")
    if not display_setup.init_display_driver():
        print("FATAL: Display hardware error!")
        print("Check SPI wiring and pins.")
        return

    print("✓ Display hardware OK\n")
    gc.collect()

    # ========================================
    # STEP 2: Create LVGL UI
    # ========================================
    print("[2/6] Creating user interface...")
    try:
        display.create_ui()
        print("✓ UI created and initialized\n")
    except Exception as e:
        print(f"FATAL: UI error: {e}")
        return

    gc.collect()

    # ========================================
    # STEP 3: WiFi Connection
    # ========================================
    print("[3/6] Connecting to WiFi...")
    connect_wifi()

    if not is_connected():
        print("WARNING: No WiFi connection!")
        print("Showing time only (without NTP sync).")
        print("Weather data not available.\n")
        # Continue without WiFi - at least shows the time
    else:
        print("✓ WiFi connected\n")

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
    else:
        print("[4/6] Skipping NTP (no WiFi)\n")

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
        print(f"FATAL: Timer error: {e}")
        return

    gc.collect()

    # ========================================
    # STEP 6: Main Loop
    # ========================================
    print("[6/6] Starting main loop...")
    print("=" * 50)
    print("System running! Press CTRL+C to exit.")
    print("=" * 50 + "\n")

    loop_counter = 0

    try:
        while True:
            # Run system tasks (WiFi monitoring, etc.)
            run_system_tasks()

            # LVGL task handler for event processing
            lv.task_handler()

            # Short pause
            utime.sleep_ms(50)

            # Memory info every 10 seconds
            loop_counter += 1
            if loop_counter >= 200:  # 200 * 50ms = 10s
                mem_free = gc.mem_free()
                print(f"[INFO] Free memory: {mem_free} Bytes")
                loop_counter = 0
                gc.collect()

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
        print("\nProgram terminated.")
