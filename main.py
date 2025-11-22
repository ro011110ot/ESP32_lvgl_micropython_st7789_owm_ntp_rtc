"""
main.py - Hauptprogramm für ESP32 Wetterstation mit LVGL
Koordiniert Display, WLAN, NTP und Sensordaten
"""

# Standard Library
import utime
import gc
import lvgl as lv

# Local Application
from ntp import set_rtc_from_ntp
from own_timers import start_timer_tasks
from system_tasks import run_system_tasks
from wifi import connect_wifi, is_connected
import display_setup
import display


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

            # LVGL Task Handler für Event-Verarbeitung
            lv.task_handler()

            # Kurze Pause
            utime.sleep_ms(50)

            # Alle 10 Sekunden Speicher-Info
            loop_counter += 1
            if loop_counter >= 200:  # 200 * 50ms = 10s
                mem_free = gc.mem_free()
                print(f"[INFO] Freier Speicher: {mem_free} Bytes")
                loop_counter = 0
                gc.collect()

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
