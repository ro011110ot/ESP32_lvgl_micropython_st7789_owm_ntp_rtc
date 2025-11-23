"""
main.py - Hauptprogramm für ESP32 Wetterstation mit LVGL
Koordiniert Display, WLAN, NTP und Sensordaten
"""

import gc

import lvgl as lv
# Standard Library
import utime
from fs_driver import fs_register

import display
import display_setup
# Local Application
from ntp import set_rtc_from_ntp
from own_timers import start_timer_tasks
from system_tasks import run_system_tasks
from wifi import connect_wifi, is_connected


def main():
    """
    Haupteinstiegspunkt und Logik für die Anwendung.
    """
    print("\n" + "=" * 50)
    print("ESP32 Wetterstation mit LVGL gestartet")
    print("=" * 50 + "\n")

    # ========================================
    # SCHRITT 1: Display-Hardware initialisieren
    # ========================================
    print("[1/6] Initialisiere Display-Hardware...")
    if not display_setup.init_display_driver():
        print("FATAL: Display-Hardwarefehler!")
        print("Prüfe SPI-Verkabelung und Pins.")
        return

    print("✓ Display-Hardware OK\n")
    gc.collect()

    # ========================================
    # SCHRITT 2: LVGL UI erstellen
    # ========================================
    print("[2/6] Erstelle Benutzeroberfläche...")

    fs_drv = lv.fs_drv_t()  # 1. Create the driver instance
    fs_register(fs_drv, "S")  # 2. Register it with the letter "S"

    try:
        display.create_ui()
        print("✓ UI erstellt und initialisiert\n")
    except Exception as e:
        print(f"FATAL: UI-Fehler: {e}")
        return

    gc.collect()

    # ========================================
    # SCHRITT 3: WLAN-Verbindung
    # ========================================
    print("[3/6] Verbinde mit WLAN...")
    connect_wifi()

    if not is_connected():
        print("WARNUNG: Keine WLAN-Verbindung!")
        print("Zeige nur Uhrzeit (ohne NTP-Sync).")
        print("Wetterdaten nicht verfügbar.\n")
        # Weiter ohne WLAN - zeigt zumindest die Zeit
    else:
        print("✓ WLAN verbunden\n")

    gc.collect()

    # ========================================
    # SCHRITT 4: NTP-Zeit synchronisieren
    # ========================================
    if is_connected():
        print("[4/6] Synchronisiere Zeit via NTP...")
        try:
            set_rtc_from_ntp()
            print("✓ Zeit synchronisiert\n")
        except Exception as e:
            print(f"WARNUNG: NTP-Sync fehlgeschlagen: {e}")
            print("Verwende System-Zeit.\n")
    else:
        print("[4/6] Überspringe NTP (kein WLAN)\n")

    gc.collect()

    # ========================================
    # SCHRITT 5: Hardware-Timer starten
    # ========================================
    print("[5/6] Starte Hardware-Timer...")
    try:
        start_timer_tasks()
        print("✓ Timer gestartet:")
        print("  - Display-Update: alle 1s")
        print("  - Wetter-Update: alle 15min\n")
    except Exception as e:
        print(f"FATAL: Timer-Fehler: {e}")
        return

    gc.collect()

    # ========================================
    # SCHRITT 6: Hauptschleife
    # ========================================
    print("[6/6] Starte Hauptschleife...")
    print("=" * 50)
    print("System läuft! Drücke CTRL+C zum Beenden.")
    print("=" * 50 + "\n")

    loop_counter = 0

    try:
        while True:
            # System-Tasks ausführen (WiFi-Überwachung, etc.)
            run_system_tasks()

            # Kurze Pause - LVGL wird vom Timer aktualisiert
            utime.sleep_ms(100)

    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("Programm durch Benutzer beendet (CTRL+C)")
        print("=" * 50)

    except Exception as e:
        print("\n" + "=" * 50)
        print(f"FATAL: Unerwarteter Fehler in Hauptschleife:")
        print(f"  {e}")
        print("=" * 50)
        import sys

        sys.print_exception(e)


# ========================================
# PROGRAMMSTART
# ========================================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\n" + "=" * 50)
        print("KRITISCHER FEHLER BEIM START:")
        print(f"  {e}")
        print("=" * 50)
        import sys

        sys.print_exception(e)
    finally:
        print("\nProgramm beendet.")
