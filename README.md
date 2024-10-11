# AlarmBoard für Berufsfeuerwehrtage

## Projektübersicht

Das **AlarmBoard** ist eine Webanwendung für **Berufsfeuerwehrtage bei Jugendfeuerwehren**. Es simuliert Alarmierungen und ermöglicht die Verwaltung von Einsätzen und Einsatzfahrzeugen. Die Anwendung unterstützt auch Funk-basierte Alarmierung über **Meshtastic**.

### Hauptfunktionen:
- **Einsatzverwaltung und Alarmierung** über eine Weboberfläche.
- **Netzwerkweite Anzeige** für alle Geräte im Netzwerk.
- **Diashow und Gruppeneinteilung** in Alarmpausen.
- **Meshtastic-Integration** für Funk-basierte Alarme.
- **Audiovisuelle Alarmierung** mit automatischer Tonwiedergabe.

---

## Installation

### Voraussetzungen:
- Raspberry Pi (mit Raspbian OS)
- Python 3 und pip
- Git

### Installationsschritte:

1. **Repository klonen**:

   ```bash
   git clone https://github.com/DO5JWA/AlarmBoard.git
   cd AlarmBoard
Installationsskript ausführen:
bash
Code kopieren
./install_script.sh
Anwendung starten:
bash
Code kopieren
python3 app.py
Zugriff auf die Weboberfläche:
Alarmeingabe: http://<Deine-Raspberry-Pi-IP>:5000
Alarmmonitor: http://<Deine-Raspberry-Pi-IP>:5000/monitor.html
Anpassungen

Fahrzeuge ändern:
Fahrzeuge sind in der Datei index.html definiert. Du kannst neue Fahrzeuge hinzufügen oder bestehende ändern.
Eigene Bilder für die Diashow:
Lade deine Bilder in den Ordner static/bilder, um sie in der Diashow anzuzeigen.
Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Es ermöglicht dir, den Code zu verwenden und anzupassen.

