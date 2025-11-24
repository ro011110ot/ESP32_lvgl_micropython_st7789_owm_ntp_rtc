"""
This module handles NTP time synchronization for MicroPython.

It provides a function to set the ESP32's Real-Time Clock (RTC) to the
correct local time for Central European Time (CET/CEST), including daylight
saving adjustments.
"""

import time

import ntptime
from machine import RTC


def set_rtc_from_ntp():
    """
    Fetches time from an NTP server, calculates the corresponding CET/CEST local time,
    and sets the ESP32's hardware RTC to that local time.
    """
    try:
        # 1. Synchronize the system time to UTC from an NTP server.
        # This updates time.time() and time.localtime() to UTC.
        ntptime.settime()

        # 2. Get the correct local time tuple using the cettime logic.
        local_time_tuple = cettime()

        # 3. Set the hardware RTC to the calculated local time.
        rtc = RTC()
        rtc.datetime(local_time_tuple)

        print("RTC successfully synchronized to local time (CET/CEST).")
    except Exception as e:
        print(f"Failed to set RTC from NTP: {e}")
        # Re-raise the exception or handle it as appropriate for the application
        raise


def cettime():
    """
    Calculates the current Central European Time (CET/CEST) including daylight saving.

    This function assumes the system clock has been previously set to UTC
    (e.g., by `ntptime.settime()`).

    Returns:
        tuple: A tuple formatted for `machine.RTC().datetime()`:
               (year, month, day, weekday, hour, minute, second, subsecond)
               Note: weekday is 1-7 (Monday-Sunday) for RTC.datetime().
    """
    year = time.localtime()[0]

    # Determine DST start and end times for the current year in Europe.
    # DST starts on the last Sunday of March (at 1:00 UTC, which is 2:00 CET)
    # Formula for last Sunday of a month: (31 - (int(5 * year / 4 + X)) % 7)
    # For March (month 3), X=4. For October (month 10), X=1.
    dst_start_utc = time.mktime(
        (year, 3, (31 - (int(5 * year / 4 + 4)) % 7), 1, 0, 0, 0, 0)
    )
    # DST ends on the last Sunday of October (at 1:00 UTC, which is 2:00 CEST)
    dst_end_utc = time.mktime(
        (year, 10, (31 - (int(5 * year / 4 + 1)) % 7), 1, 0, 0, 0, 0)
    )

    now_utc = time.time()

    # Apply timezone offset based on whether DST is active
    if dst_start_utc <= now_utc < dst_end_utc:
        # CEST: Central European Summer Time (UTC+2 hours)
        offset_seconds = 7200
    else:
        # CET: Central European Time (UTC+1 hour)
        offset_seconds = 3600

    # Convert UTC time to local time with the determined offset
    cet_tuple = time.localtime(now_utc + offset_seconds)

    # `time.localtime()` returns: (year, month, mday, hour, minute, second, weekday_0_6, yearday)
    # `machine.RTC.datetime()` expects: (year, month, mday, weekday_1_7, hour, minute, second, microsecond)
    # Note: `time.localtime()` weekday is 0-6 (Monday=0, Sunday=6).
    # `machine.RTC.datetime()` expects 1-7 (Monday=1, Sunday=7).

    year, month, day, hour, minute, second, weekday_0_6, _ = cet_tuple

    # Adjust weekday format for the RTC
    weekday_1_7 = weekday_0_6 + 1

    # Create the tuple in the format expected by RTC.datetime()
    rtc_tuple = (year, month, day, weekday_1_7, hour, minute, second, 0)

    return rtc_tuple