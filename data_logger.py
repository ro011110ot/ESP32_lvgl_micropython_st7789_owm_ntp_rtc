"""
Dieses Modul protokolliert Wetterdaten in einer CSV-Datei.

(Die Protokollierung des DHT-Sensors wurde entfernt.)
"""

# Standard Library
import os
import utime

# --- KONSTANTEN ---
LOG_DIR = "/temp_history"
LOG_FILE = LOG_DIR + "/weather_log.csv"
# Header aktualisiert: Nur OWM-Daten
HEADER = "timestamp,temp_owm,pressure_owm,humi_owm,windspeed_owm,winddeg_owm,weather_desc"


def ensure_log_directory():
    """Stellt sicher, dass das Protokollverzeichnis auf dem Dateisystem existiert."""
    try:
        os.mkdir(LOG_DIR)
    except OSError as e:
        # Fehler 17 (EEXIST) ist normal, wenn das Verzeichnis bereits existiert.
        if e.args[0] != 17:
            print("Fehler beim Erstellen des Protokollverzeichnisses:", e)


def log_data(owm_data):
    """
    Schreibt Wetterdaten (OWM) in die CSV-Datei.

    Args:
        owm_data (tuple): Ein Tupel mit Wetterdaten von der OWM-API.
    """
    # 1. Sicherstellen, dass das Verzeichnis existiert
    ensure_log_directory()

    # 2. Zeitstempel vorbereiten
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

    # 3. Daten zu einer Zeile zusammenführen
    data_row = (timestamp,) + owm_data

    # 4. Erstellt die kommagetrennte Zeichenkette
    data_line = ",".join(str(x) if x is not None else "" for x in data_row)

    # 5. In die Datei schreiben und ggf. Header hinzufügen
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
        print("Fehler beim Schreiben der Protokolldatei:", e)
