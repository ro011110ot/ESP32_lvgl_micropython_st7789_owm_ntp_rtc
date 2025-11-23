"""
This module handles NTP time synchronization.

It provides a function to set the ESP32's Real-Time Clock (RTC) to the
correct local time for Central European Time (CET/CEST), including daylight
saving adjustments.
"""

# Standard Library
import time

# Third-Party
import ntptime
from machine import RTC


def set_rtc_from_ntp():
    """
    Fetches time from NTP, calculates the corresponding CET/CEST local time,
    and sets the RTC to that local time.
    """
    try:
        # 1. Sync system time to UTC from NTP server
        ntptime.settime()

        # 2. Get the correct local time tuple using the cettime logic
        local_time_tuple = cettime()

        # 3. Set the hardware RTC to the calculated local time
        rtc = RTC()
        rtc.datetime(local_time_tuple)

        print("RTC successfully synchronized to local time (CET/CEST).")
    except Exception as e:
        print(f"Failed to set RTC from NTP: {e}")


def cettime():
    """
    Calculates the current Central European Time (CET/CEST) including daylight saving.

    This function assumes the system clock is set to UTC.

    Returns:
        A tuple formatted for `machine.RTC().datetime()`:
        (year, month, day, weekday, hour, minute, second, subsecond)
    """
    year = time.localtime()[0]

    # Determine DST start and end times for the current year in Europe
    # DST starts on the last Sunday of March
    dst_start = time.mktime(
        (year, 3, (31 - (int(5 * year / 4 + 4)) % 7), 1, 0, 0, 0, 0, 0)
    )
    # DST ends on the last Sunday of October
    dst_end = time.mktime(
        (year, 10, (31 - (int(5 * year / 4 + 1)) % 7), 1, 0, 0, 0, 0, 0)
    )

    now_utc = time.time()

    if now_utc < dst_start:
        # CET: UTC+1H
        cet_tuple = time.localtime(now_utc + 3600)
    elif now_utc < dst_end:
        # CEST: UTC+2H
        cet_tuple = time.localtime(now_utc + 7200)
    else:
        # CET: UTC+1H
        cet_tuple = time.localtime(now_utc + 3600)

    # time.localtime() returns: (year, month, mday, hour, minute, second, weekday, yearday)
    # machine.RTC.datetime() expects: (year, month, mday, weekday, hour, minute, second, microsecond)
    # The weekday format also differs. time.localtime() is 0-6 (Mon-Sun).
    # The user's original code implies their RTC expects 1-7.

    year, month, day, hour, minute, second, weekday_0_6, _ = cet_tuple

    # Adjust weekday format for the RTC
    weekday_1_7 = weekday_0_6 + 1

    # Create the tuple in the format expected by RTC.datetime()
    rtc_tuple = (year, month, day, weekday_1_7, hour, minute, second, 0)

    return rtc_tuple
