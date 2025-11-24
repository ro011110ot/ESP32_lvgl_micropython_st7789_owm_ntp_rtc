"""
boot.py - Executed on every boot.

This file is automatically executed by MicroPython on every boot,
including wake-boot from deep sleep. It's the ideal place for
initial setup that should run before main.py, such as:
- Setting up OS debugging.
- Starting the WebREPL (Web-based Python Prompt).
- Configuring essential hardware settings.
"""

# Uncomment the following lines to enable specific features:

# import esp
# esp.osdebug(None)  # Disable OS debug output

# import webrepl
# webrepl.start()  # Start the WebREPL daemon