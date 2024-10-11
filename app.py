from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from gtts import gTTS
import json
import meshtastic
import meshtastic.serial_interface
import os
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Einsatz Mapping für Präfixe
einsatz_prefix_mapping = {
    "B:": "Brand",
    "H:": "Hilfeleistung"
}

# Funktion zum Verarbeiten der Einsatzstichwörter basierend auf Präfixen (nur für Sprachausgabe)
def process_einsatz_text_for_tts(einsatz_text):
    for prefix, full_text in einsatz_prefix_mapping.items():
        if einsatz_text.startswith(prefix):
            einsatz_text = einsatz_text.replace(prefix, full_text, 1)  # Nur das erste Vorkommen ersetzen
            break
    return einsatz_text

# Funktion zum Laden der letzten Einsatznummer
def load_last_einsatznummer():
    try:
        if os.path.exists('einsatznummer.txt'):
            with open('einsatznummer.txt', 'r') as file:
                return int(file.read().strip())
        else:
            return 0
    except Exception as e:
        print(f"Fehler beim Laden der Einsatznummer: {e}")
        return 0

# Funktion zum Speichern der neuen Einsatznummer
def save_new_einsatznummer(einsatznummer):
    try:
        with open('einsatznummer.txt', 'w') as file:
            file.write(str(einsatznummer))
    except Exception as e:
        print(f"Fehler beim Speichern der Einsatznummer: {e}")

# Funktion zum Senden von Nachrichten über Meshtastic
def send_meshtastic_message(message):
    try:
        interface = meshtastic.serial_interface.SerialInterface()
        interface.sendText(message, channelIndex=3)
        interface.close()
    except Exception as e:
        print(f"Fehler beim Senden der Meshtastic-Nachricht: {e}")

# Funktion zum Schreiben in die Protokolldatei
def log_event(event_type, data, einsatznummer):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    log_filename = f"logs/einsatz_{einsatznummer}.log"
    log_message = f"{timestamp}\t{event_type}\t{json.dumps(data, ensure_ascii=False)}\n"

    if not os.path.exists('logs'):
        os.makedirs('logs')

    with open(log_filename, 'a') as log_file:
        log_file.write(log_message)

# Route zum Rendern von index.html
@app.route('/')
def index():
    return render_template('index.html')

# Route zum Rendern von monitor.html
@app.route('/monitor')
def monitor():
    return render_template('monitor.html')

# Route für die Diashow-Seite
@app.route('/diashow')
def diashow():
    return render_template('diashow.html')

# Route für die Gruppenübersicht-Seite
@app.route('/gruppen')
def gruppen():
    return render_template('gruppen.html')


# Route für das Auslösen eines Alarms
@app.route('/submit', methods=['POST'])
def submit_alarm():
    alarm_data = request.get_json()

    # Verarbeite den Einsatztext nur für die Sprachausgabe
    einsatz_text_for_tts = process_einsatz_text_for_tts(alarm_data['einsatz'])

    # Einsatznummer laden und erhöhen
    einsatznummer = load_last_einsatznummer() + 1
    save_new_einsatznummer(einsatznummer)

    # Erstelle die TTS nur mit dem umgewandelten Text
    tts_text = f"Alarm für die Feuerwehr: {einsatz_text_for_tts}, {alarm_data['ort']}, Einsatzfahrzeuge: {alarm_data['fahrzeuge']}."
    
    try:
        print(f"Sprachausgabe-Text: {tts_text}")  # Debugging

        tts = gTTS(tts_text, lang='de')
        tts.save('static/alarm_tts.mp3')
    except Exception as e:
        return jsonify({"status": "error", "message": "Fehler beim Erstellen der TTS-Datei"}), 500

    # Meshtastic Nachricht senden (mit ursprünglichem Text für B: und H:)
    send_meshtastic_message(f"Alarm ausgelöst! {alarm_data['einsatz']} in {alarm_data['ort']} mit {alarm_data['fahrzeuge']}")

    # Sende den Alarm an alle Clients, aber mit dem ursprünglichen Text
    socketio.emit('new_alarm', alarm_data, broadcast=True)
    log_event("Alarm ausgelöst", alarm_data, einsatznummer)

    return jsonify({"status": "success", "message": "Alarm ausgelöst"})

# Route für die Nachalarmierung
@app.route('/nachalarm', methods=['POST'])
def nachalarm():
    nachalarm_data = request.get_json()

    # Verarbeite den Einsatztext nur für die Sprachausgabe
    einsatz_text_for_tts = process_einsatz_text_for_tts(nachalarm_data['einsatz'])

    # Einsatznummer laden
    einsatznummer = load_last_einsatznummer()

    # Erstelle die TTS nur mit dem umgewandelten Text
    tts_text = f"Nachalarmierung der Feuerwehr für den Einsatz: {einsatz_text_for_tts}, {nachalarm_data['ort']}, Nachalarmierte Fahrzeuge: {nachalarm_data['fahrzeuge']}."
    
    try:
        print(f"Sprachausgabe-Text: {tts_text}")  # Debugging der Sprachausgabe

        tts = gTTS(tts_text, lang='de')
        tts.save('static/nachalarm_tts.mp3')  # Nachalarm-TTS-Datei speichern
    except Exception as e:
        return jsonify({"status": "error", "message": "Fehler beim Erstellen der Nachalarm-TTS-Datei"}), 500

    # Meshtastic Nachricht senden (mit ursprünglichem Text für B: und H:)
    send_meshtastic_message(f"Nachalarm! {nachalarm_data['einsatz']} in {nachalarm_data['ort']} mit {nachalarm_data['fahrzeuge']}")

    # Sende den Nachalarm an alle Clients, aber mit dem ursprünglichen Text
    socketio.emit('new_nachalarm', nachalarm_data, broadcast=True)
    log_event("Nachalarmierung", nachalarm_data, einsatznummer)

    return jsonify({"status": "success", "message": "Nachalarmierung erfolgreich ausgelöst"})

# Route für das Beenden eines Einsatzes
@app.route('/end_alarm', methods=['POST'])
def end_alarm():
    try:
        # Beende den Einsatz, indem eine Nachricht über SocketIO gesendet wird
        socketio.emit('einsatz_beendet', broadcast=True)
        return jsonify({"status": "success", "message": "Einsatz beendet"})
    except Exception as e:
        return jsonify({"status": "error", "message": "Fehler beim Beenden des Einsatzes"}), 500

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
