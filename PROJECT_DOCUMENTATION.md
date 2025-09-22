# WIZARD-2.1 - Business Application Dokumentation

## Projektübersicht
- **Projektname**: WIZARD-2.1
- **Typ**: Desktop-Anwendung
- **Programmiersprache**: Python
- **Ziel**: Business Application auf Unternehmensniveau

## Technologie-Stack
- **Frontend Framework**: PyQt6
- **UI-Design**: Qt Designer (.ui Dateien)
- **Backend**: Python
- **Datenverarbeitung**: pandas (DataFrame für Temperaturdaten)
- **TOB-Verarbeitung**: tob-dataloader (Version 1.1.2)
- **Visualisierung**: matplotlib (Linien-Diagramme)
- **Projekt-Speicherung**: Verschlüsselte .wzp Dateien (keine separate Datenbank)
- **Projekt-Verschlüsselung**: AES-256 Verschlüsselung mit app-internem Schlüssel (keine User-Passwörter)
- **Architektur**: MVC (Model-View-Controller)
- **Plattform**: Cross-Platform (macOS, Windows, Linux)
- **Entwicklungsumgebung**: macOS

## Projektstruktur
```
WIZARD-2.1/
├── src/
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── tob_data_model.py
│   │   └── project_model.py
│   ├── views/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   └── dialogs/
│   │       ├── __init__.py
│   │       ├── error_dialogs.py
│   │       ├── project_dialogs.py
│   │       ├── progress_dialogs.py
│   │       └── processing_list_dialog.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── main_controller.py
│   │   └── tob_controller.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── tob_service.py
│   │   ├── data_service.py
│   │   ├── error_service.py
│   │   └── encryption_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── helpers.py
│   │   ├── logging_config.py
│   │   └── error_handler.py
│   └── exceptions/
│       ├── __init__.py
│       ├── tob_exceptions.py
│       ├── database_exceptions.py
│       └── server_exceptions.py
├── ui/
│   └── *.ui (Qt Designer Dateien)
├── resources/
│   ├── icons/
│   ├── images/
│   ├── styles/
│   └── translations/
│       ├── wizard_en_US.ts
│       ├── wizard_de_DE.ts
│       ├── wizard_en_US.qm
│       └── wizard_de_DE.qm
├── tob_dataloader/ (TOB DataLoader Package)
├── tests/
│   ├── unit/
│   ├── integration/
│   └── ui/
├── docs/
│   ├── api/
│   ├── user_guide/
│   └── developer/
├── logs/ (Log-Dateien - automatisch erstellt)
├── data/ (Beispiel .TOB Dateien)
├── ~/.wizard/ (User-Daten - automatisch erstellt)
│   ├── projects/ (Verschlüsselte .wzp Projektdateien)
│   ├── settings/ (Nur Spracheinstellung)
│   └── cache/ (Temporäre Dateien)
├── requirements.txt (Python Dependencies)
├── requirements-dev.txt (Development Dependencies)
├── .pre-commit-config.yaml
├── .pylintrc
├── .black
├── mypy.ini (Type Checker Konfiguration)
├── build/ (Build-Artefakte)
├── dist/ (Distribution-Pakete)
├── .github/workflows/ (CI/CD Pipeline)
├── README.md
└── PROJECT_DOCUMENTATION.md
```

## Anforderungen

### Funktionale Anforderungen
- **Anwendungsbereich**: Wissenschaftliches Unternehmen (FIELAX)
- **Hauptfunktion**: Temperaturdaten-Analyse und Visualisierung
- **Datenformat**: .TOB Dateien (Text-basiert, wissenschaftliche Daten)
- **Bestehende Verarbeitung**: TOB DataLoader Package (Version 1.1.2)
  - Header → Dictionary
  - Temperaturdaten → pandas DataFrame
- **UI-Features** (bereits implementiert):
  - Welcome-Screen mit TOB/Projekt-Öffnung
  - NTC-Sensor-Auswahl (PT100, NTC01-NTC22)
  - Plot-Container für Datenvisualisierung
  - Achsen-Kontrolle (X, Y1, Y2) mit Auto/Manual-Modus
  - Datenmetriken-Anzeige (HP-Power, Vaccu, Tilt, Press)
  - Projekt-Kontrolle (Subcon, Quality Control, Send Data)
  - Internationalisierung (Englisch/Deutsch)
  - Menü-System (File, Project, Tools)

### Nicht-funktionale Anforderungen
- **TOB-Datei Workflow**:
  - Nach dem Laden einer .TOB Datei: Dialog "Projekt anlegen?" oder "Nur Diagramm anzeigen?"
  - Standardmäßig alle NTC-Sensoren im Plot anzeigen
  - NTC-Checkboxen in Sidebar steuern Sichtbarkeit im Plot (enabled/disabled)
  - Live-Update des Plots bei Checkbox-Änderungen
- **Projekt-Management**:
  - Projekt speichert alle Daten in verschlüsselter .wzp Datei (AES-256, app-interner Schlüssel)
  - Projekt enthält: Metadaten, Server-Konfiguration, zukünftig .TOB Daten
  - Projekt-Erstellung mit Server-Konfiguration im gleichen Dialog
  - Projekt-Settings können später bearbeitet werden (Menü: Project → Edit Project Settings)
  - Visual Check durch User vor Server-Übertragung
  - cURL-Befehl an Server mit .TOB Daten
  - Server-Antwort mit Informationen über .TOB Datei

### Benutzerrollen & Berechtigungen
- [ ] Zu definieren

### Projekt-Datenmodell (.wzp Datei)
- **Projekt-Metadaten**:
  - Name (Projekt-Name)
  - Description (Projekt-Beschreibung)
  - Created_Date (Erstellungsdatum)
  - Modified_Date (Letzte Änderung)
  - Version (Projekt-Version)
  - Status (Draft, Ready, Sent, Processed)
- **Server-Konfiguration** (integriert bei Projekt-Erstellung):
  - URL (Server-URL für API-Kommunikation)
  - Bearer_Token (Enter-Key für Server-Authentifizierung)
  - Project_Field_Name (cURL Form-Feld für Projekt)
  - Location_Field_Name (cURL Form-Feld für Location)
  - TOB_File_Field_Name (cURL Form-Feld für TOB-Datei)
  - Subconn_Length_Field_Name (cURL Form-Feld für Subcon)
  - String_ID_Field_Name (cURL Form-Feld für String-ID)
  - Comment_Field_Name (cURL Form-Feld für Kommentar)
- **TOB-Datei-Informationen**:
  - File_Path (Original .TOB Datei)
  - File_Name (Dateiname)
  - File_Size (Dateigröße)
  - Header_Data (JSON mit Header-Informationen)
  - Data_Count (Anzahl Datensätze)
  - Loaded_Date (Lade-Datum)
  - Processing_Status (Loaded, Processed, Sent)
  - Display_Order (Anzeige-Reihenfolge in Processing List)
  - Is_Active (Aktuell im Plot-Frame angezeigt)
  - Last_Accessed (Letzter Zugriff)
- **TOB-Daten**:
  - Raw_Data (Komplette .TOB Daten als JSON/CSV)
  - Processed_Data (Verarbeitete Sensordaten)
  - Timestamps (Zeitstempel-Array)
  - Sensor_Data (NTC01-NTC22, PT100, VBATT, PRESS, etc.)
  - Heat_Pulse_Data (Hitzepuls-Informationen)
- **Server-Kommunikation**:
  - Job_ID (Server Job-ID nach Upload)
  - Server_Status (Status vom Server)
  - Sensor_Qualities (JSON mit Sensor-Qualitäten)
  - Last_Upload_Date (Letzter Upload)
  - Upload_History (Historie der Uploads)

## Architektur-Entscheidungen
- [x] Frontend Framework: PyQt6
- [x] UI-Design: Qt Designer (.ui Dateien)
- [x] Projekt-Speicherung: Verschlüsselte .wzp Dateien (keine separate Datenbank)
- [x] Projekt-Verschlüsselung: App-interne AES-256 Verschlüsselung (keine User-Passwörter)
- [x] Architektur-Pattern: MVC (Model-View-Controller)
- [x] Python Version: 3.13.7 (neueste stabile Version)
- [x] Package Manager: pip mit requirements.txt (für einfaches Dependency Management)
- [x] Code Quality Tools: Black, Pylint, Sphinx
- [x] Logging-Strategie: Strukturiertes Logging mit konfigurierbaren Levels
- [x] Type Hints: Vollständige Typisierung für alle Funktionen und Klassen
- [x] Konfigurationsmanagement: Keine - Anwendung verwendet Standard-Einstellungen
- [ ] Server-Kommunikation: cURL für .TOB Daten-Übertragung

## Entwicklungsumgebung
- **Entwicklungsplattform**: macOS (darwin 24.6.0)
- **Python Version**: 3.13.7 (neueste stabile Version)
- **IDE/Editor**: VS Code / PyCharm (empfohlen)
- **Versionskontrolle**: Git
- **Package Manager**: pip mit requirements.txt (für einfaches Dependency Management)
- **Cross-Platform Testing**: GitHub Actions CI/CD

## Deployment & Distribution
- [x] **Cross-Platform Packaging**: PyInstaller für alle Plattformen
- [x] **Installer-Erstellung**:
  - **macOS**: .dmg Installer mit Code-Signing
  - **Windows**: .exe Installer mit Code-Signing
  - **Linux**: .deb (Debian/Ubuntu) und .rpm (Red Hat/Fedora) Pakete
- [x] **Update-Mechanismus**: Automatische Update-Prüfung mit manueller Installation
- [x] **Code-Signing**: Für alle Plattformen (macOS, Windows, Linux)
- [x] **Dependency-Bundling**: Alle Python-Dependencies in ausführbare Datei eingebettet
- [x] **Cross-Platform Testing**: GitHub Actions für alle Zielplattformen

### Cross-Platform Deployment Details
- **PyInstaller Konfiguration**:
  - **One-File Mode**: Einzelne ausführbare Datei pro Plattform
  - **Hidden Imports**: Automatische Erkennung aller Dependencies
  - **Data Files**: UI-Dateien, Übersetzungen, Icons eingebettet
  - **Icon-Set**: Plattform-spezifische Icons (.ico, .icns, .png)
- **Plattform-spezifische Builds**:
  - **macOS**: 
    - .app Bundle mit Code-Signing
    - .dmg Installer mit Drag & Drop Installation
    - Notarization für Gatekeeper-Kompatibilität
  - **Windows**:
    - .exe Installer mit NSIS/Inno Setup
    - Windows Defender Kompatibilität
    - Code-Signing mit Authenticode
  - **Linux**:
    - .deb Pakete für Debian/Ubuntu
    - .rpm Pakete für Red Hat/Fedora
    - AppImage für universelle Kompatibilität
- **Dependency-Management**:
  - **Python Runtime**: Eingebettet in ausführbare Datei
  - **System Libraries**: Automatische Erkennung und Einbettung
  - **Qt Libraries**: PyQt6 Runtime eingebettet
  - **Scientific Libraries**: NumPy, Pandas, Matplotlib eingebettet
- **Installation-Verzeichnisse**:
  - **macOS**: `/Applications/Wizard-2.1.app`
  - **Windows**: `C:\Program Files\Wizard-2.1\`
  - **Linux**: `/opt/wizard-2.1/` oder User-Home
- **User-Data-Verzeichnisse**:
  - **macOS**: `~/Library/Application Support/Wizard-2.1/`
  - **Windows**: `%APPDATA%\Wizard-2.1\`
  - **Linux**: `~/.local/share/wizard-2.1/`
- **Minimale Konfiguration**:
  - **Keine komplexen Einstellungen**: Anwendung verwendet Standard-Werte
  - **Nur Spracheinstellung**: Einzige persistente Benutzereinstellung
  - **Standard-Verhalten**: Alle anderen Einstellungen sind hardcoded
- **Keine Backup-Strategie**:
  - **Keine automatischen Backups**: Nicht benötigt
  - **Keine Datenwiederherstellung**: Nicht implementiert
  - **User-Responsibility**: Benutzer ist für eigene Backups verantwortlich

## Sicherheit
- [ ] Authentifizierung
- [ ] Autorisierung
- [ ] Datenverschlüsselung
- [ ] Audit-Logging

## Testing-Strategie
- [x] **Unit Tests**: pytest für alle Business Logic
- [x] **Integration Tests**: pytest für Datenbank und Server-Kommunikation
- [x] **UI Tests**: pytest-qt für PyQt6 UI-Tests
- [x] **Code Coverage**: pytest-cov für Coverage-Berichte
- [x] **Test Data**: Beispiel .TOB Dateien für Tests

## Dokumentation
- [x] **API-Dokumentation**: Sphinx mit automatischer Generierung aus Docstrings
- [x] **Benutzerhandbuch**: Sphinx mit Screenshots und Anleitungen
- [x] **Entwickler-Dokumentation**: Sphinx mit Architektur und Code-Dokumentation
- [x] **Code-Dokumentation**: Google-Style Docstrings für alle Funktionen und Klassen

## Meilensteine & Timeline
- [ ] Projekt-Setup
- [ ] Grundarchitektur
- [ ] Core-Features
- [ ] Testing
- [ ] Deployment

## Notizen & Entscheidungen

### Cross-Platform Anforderungen
- **Zielplattformen**: macOS, Windows, Linux
- **Entwicklungsumgebung**: macOS (darwin 24.6.0)
- **Wichtige Überlegungen**:
  - UI-Framework muss plattformübergreifend funktionieren
  - Pfad-Handling muss OS-agnostisch sein
  - Dateisystem-Unterschiede berücksichtigen
  - Plattform-spezifische Features optional implementieren

### Frontend Framework Entscheidung
- **Gewählt**: PyQt6
- **UI-Design**: Qt Designer (.ui Dateien) - bereits vorhanden
- **Vorteile**:
  - Professionelle Business-Anwendung
  - Native Look & Feel auf allen Plattformen
  - Mächtige Widgets und Layout-Manager
  - Ausgezeichnete Cross-Platform-Unterstützung
  - Qt Designer für visuelles UI-Design

### UI-Struktur Analyse (bereits implementiert)
- **Hauptfenster**: 1374x776 Pixel, Minimum 1110x600
- **Layout**: Grid-Layout mit 3 Hauptbereichen
  - **Plot-Container**: Hauptbereich für Datenvisualisierung
    - Plot-Info-Container: Project/Location Info, Logo, Location-Combo
    - Plot-Canvas-Container: Für matplotlib/Plotting-Widgets
    - Welcome-Container: Zentrierte Begrüßung mit TOB/Projekt-Buttons
  - **Sidebar**: NTC-Sensor-Auswahl (PT100, NTC01-NTC22) und Sensor-String-Bild
  - **Bottom-Container**: 
    - Datenmetriken: Mean HP-Power, Max Vaccu, Tilt Status, Mean Press
    - Achsen-Kontrolle: X, Y1, Y2 mit Auto/Manual-Modus und Min/Max-Werten
      - Y1: Temperatur-Sensoren (NTCs, PT100)
      - Y2: Weitere Sensoren (XTilt, YTilt, VBATT, PRESS, etc.)
    - Projekt-Kontrolle: Subcon, Comment, Sensor String, Quality Control, Send Data
- **Menü-System**: File, Project, Tools mit Untermenüs
  - File: Open, Show Header & Info, Exit
  - Project: Create/Open Project File, Edit Settings, Show Processing List
  - Tools: Language (EN/DE), Sidebar Toggle, NTC Select/Deselect All
- **Processing List Dialog**:
  - **Zugriff**: Menübar → Project → Show Processing List
  - **Funktion**: Übersicht aller .TOB Dateien im aktuellen Projekt
  - **Anzeige**: Tabellarische Liste mit TOB-Datei-Informationen
  - **Spalten**: Dateiname, Dateigröße, Lade-Datum, Status, Server-Status, Aktionen
  - **Aktionen**: Datei anzeigen, Server-Status abfragen, Datei entfernen
  - **Filter**: Nach Status, Datum, Dateigröße filtern
  - **Sortierung**: Nach Spalten sortierbar (aufsteigend/absteigend)
  - **Kontext-Menü**: Rechtsklick für zusätzliche Aktionen
- **Styling**: Grüner Hintergrund (#3AAA35), weiße Container

### Wissenschaftliche Datenverarbeitung
- **Datenformat**: .TOB Dateien (Text-basiert) und .FLX Dateien (JSON+CSV)
- **Verarbeitung**: TOB DataLoader Package (Version 1.1.2)
  - Header-Informationen → Python Dictionary
  - Temperaturdaten → pandas DataFrame
  - Auto-Detection: TOB/FLX Format
  - Optional: Timestamp-Parsing, Position-Parsing
- **Anwendungsbereich**: Wissenschaftliches Unternehmen
- **Datenanalyse**: Temperaturdaten und wissenschaftliche Messungen
- **Features**: 
  - Intelligente Header-Erkennung
  - Robuste Datenverarbeitung
  - Wissenschaftliche Notation (1.234E+0000)
  - Fehlerbehandlung mit spezifischen Exceptions

### Workflow-Details
- **TOB-Datei Laden**:
  1. User wählt .TOB Datei über File Dialog
  2. TOB DataLoader verarbeitet Datei (Header + DataFrame)
  3. Dialog: "Projekt anlegen?" oder "Nur Diagramm anzeigen?"
  4. Plot wird im plot_canvas_container angezeigt
  5. Alle NTC-Sensoren standardmäßig aktiviert
- **NTC-Sensor-Steuerung**:
  - Checkboxen in Sidebar steuern Sichtbarkeit im Plot
  - Live-Update bei Checkbox-Änderungen
  - Plot zeigt nur aktivierte Sensoren an
- **Projekt-Workflow**:
  1. User wählt "Project → Create Project File"
  2. Dialog: Projekt-Name, Enter-Key, Server-URL und Beschreibung eingeben
  3. Projekt wird automatisch mit app-interner Verschlüsselung erstellt und gespeichert (.wzp)
  4. Später: "Project → Edit Project Settings" für Bearbeitung der Projekt-Konfiguration
  5. .TOB Daten können später zum Projekt hinzugefügt werden (zukünftiges Feature)
  6. Visual Check durch User (Plot-Analyse)
  7. "Send Data" Button: cURL POST mit multipart/form-data an Server
  8. Server gibt Job-ID zurück
  9. "Request Status" Button: cURL GET mit Job-ID für Status-Abfrage
  10. Server-Antwort (JSON) mit Status und Sensor-Qualitäten wird angezeigt
- **Processing List Workflow**:
  1. User öffnet Processing List (Menübar → Project → Show Processing List)
  2. Übersicht aller .TOB Dateien im Projekt wird angezeigt
  3. User kann neue .TOB Dateien hinzufügen (Toolbar-Button oder Drag & Drop)
  4. User kann Dateien auswählen und im Plot-Frame anzeigen
  5. User kann Dateien aus dem Projekt entfernen (mit Bestätigung)
  6. User kann Server-Status für einzelne Dateien abfragen
  7. Änderungen werden automatisch in .wzp Datei gespeichert

### Datenvisualisierung
- **Plot-Typ**: Linien-Diagramm mit matplotlib
- **Haupt-Plot (Y1-Achse)**:
  - X-Achse: Zeit (aus Timestamp der .TOB Datei)
  - Y1-Achse: Temperaturwerte der NTC-Sensoren
  - Sensor-Farben:
    - NTC01-NTC07: Rot (verschiedene Linien-Stile)
    - NTC08-NTC12: Blau (verschiedene Linien-Stile)
    - NTC13-NTC22: Schwarz (verschiedene Linien-Stile)
    - PT100: Orange
- **Sub-Plot (Y2-Achse)**:
  - Unter dem Haupt-Plot
  - Weitere .TOB Daten: XTilt in °, YTilt, VBATT, PRESS, etc.
  - Gleiche X-Achse (Zeit) wie Haupt-Plot
- **Achsen-Kontrolle**:
  - Auto-Modus: Optimale Skalierung für alle Linien
  - Manual-Modus: Benutzer-definierte Min/Max-Werte
  - Linien-Stile: Solid, Dashed, Dotted, Dash-dot für Unterscheidung

### Datenmetriken-Berechnung
- **Mean HP-Power**: Durchschnittliche Heat Power aus Spannungen während Hitzepulsen
  - Berechnung nur während aktiver Hitzepulse
  - Rauschen zwischen Hitzepulsen wird ausgeschlossen
  - Verhindert Verfälschung der Durchschnittswerte
- **Max Vaccu**: Maximale Batteriespannung
- **Tilt Status**: X/Y Neigungswerte
- **Mean Press**: Durchschnittlicher Druck

### Server-Kommunikation (cURL)
- **Upload (POST)**:
  - Format: multipart/form-data
  - Headers: Content-Type, Accept: application/json, Authorization: Bearer {baerercode}
  - Form-Felder: projectName, locationName, tobFile, subcon, stringID, comment
  - Endpoint: URL aus Projekt-Konfiguration
- **Status-Abfrage (GET)**:
  - Format: GET Request
  - Headers: Accept: application/json, Authorization: Bearer {baerercode}
  - Endpoint: URL + jobID
- **Server-Antwort-Struktur**:
  - result.status: Status der Verarbeitung
  - result.quality: Qualitätsinformationen
  - result.Body.data.id: Job-ID
  - result.Body.data.status: Verarbeitungsstatus
  - result.Body.data.status_description: Status-Beschreibung
  - result.Body.data.sensor_qualities: Sensor-Qualitätsarray (JSON)
  - result.Body.message: Fehlermeldungen
  - result.CurlCode: cURL Return Code

### Code Quality & Development Standards
- **Python Version**: 3.13.7 (neueste stabile Version)
- **Code Style**: PEP 8 mit Black Formatter
- **Linting**: Pylint für Code-Analyse und Qualitätssicherung
- **Documentation**: Sphinx mit Google-Style Docstrings
- **Dependency Management**: pip mit requirements.txt für einfache Package-Verwaltung
- **Pre-commit Hooks**: Automatische Code-Formatierung und Linting
- **Testing**: pytest mit pytest-qt für UI-Tests
- **CI/CD**: GitHub Actions für Cross-Platform Testing
- **Type Hints**: Vollständige Typisierung mit mypy für statische Analyse
- **Error Handling**: Strukturierte Exception-Behandlung mit User-Dialogen
- **Logging**: Strukturiertes Logging mit Rotation und Kategorisierung
- **Code Quality**: mypy für Type Checking, Pylint für Code-Analyse
- **User Experience**: Benutzerfreundliche Error-Dialoge mit Recovery-Optionen
- **Internationalisierung**: Qt i18n mit Englisch/Deutsch und dynamischem Sprachwechsel
- **Sicherheit**: AES-256 Verschlüsselung für Projektdateien mit Passwort-Schutz
- **Cross-Platform**: PyInstaller für macOS, Windows, Linux mit Code-Signing

### TOB-Datei Analyse (Beispiel: temperaturdaten.TOB)
- **Dateigröße**: 1.2 MB (3.820 Zeilen)
- **Header-Struktur**: 
  - Software-Info: "SSDA Sea & Sun Technology's Standard Data Acquisition"
  - Projekt-Info: Ship, Station, Position, Operator, Comments
  - Sensor-Konfiguration: 33 Sensoren (NTC01-NTC22, PT100, Vbatt, Press, etc.)
- **Datenformat**: 
  - Wissenschaftliche Notation (z.B. 1.15490000000E-0002)
  - Zeitstempel: Format "HH:MM:SS.mmm DD.MM.YYYY"
  - Messwerte: Temperatur (°C), Spannung (Volt), Druck (dbar), Neigung (°)
- **Datenmenge**: ~3.750 Messpunkte mit 1-Sekunden-Intervall
- **Performance-Anforderungen**:
  - Ladezeit: < 5 Sekunden für 1.2 MB Dateien
  - Memory-Usage: < 100 MB für vollständige Datenverarbeitung
  - Plot-Rendering: < 2 Sekunden für alle Sensoren
  - Projekt-Speicherung: < 10 Sekunden für komplette .wzp Datei
  - Verschlüsselung/Entschlüsselung: < 3 Sekunden für 1.2 MB Daten

### Professional Development Tools
- **Black**: Automatische Code-Formatierung nach PEP 8
- **Pylint**: Statische Code-Analyse mit detaillierten Reports
- **Sphinx**: Automatische Dokumentationsgenerierung
- **pip**: Standard Python Package Manager mit requirements.txt
- **Pre-commit**: Automatische Code-Qualitätsprüfung vor Commits
- **pytest**: Umfassendes Testing-Framework
- **pytest-qt**: Spezielle Tests für PyQt6 Anwendungen
- **pytest-cov**: Code Coverage Berichte

### Logging-Strategie (Unternehmensstandard)
- **Logging-Framework**: Python `logging` Modul mit strukturierter Konfiguration
- **Log-Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log-Formate**: 
  - **Console**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
  - **File**: `%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s`
- **Log-Dateien**:
  - **Application Log**: `logs/wizard_app.log` (INFO, WARNING, ERROR, CRITICAL)
  - **Debug Log**: `logs/wizard_debug.log` (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - **Error Log**: `logs/wizard_error.log` (ERROR, CRITICAL)
  - **Server Communication**: `logs/wizard_server.log` (alle cURL Requests/Responses)
- **Log-Rotation**: 
  - Max. Dateigröße: 10 MB
  - Backup-Dateien: 5 Stück
  - Automatische Bereinigung nach 30 Tagen
- **Logging-Kategorien**:
  - **TOB Processing**: Datei-Laden, Header-Parsing, Datenverarbeitung
  - **Database Operations**: CRUD-Operationen, Migrationen
  - **UI Events**: Benutzer-Interaktionen, Plot-Updates
  - **Server Communication**: cURL Requests, Responses, Fehler
  - **Performance**: Ladezeiten, Memory-Usage, Plot-Rendering
- **Sensitive Data**: Keine Passwörter, Keys oder persönliche Daten in Logs

### Error Handling & User Feedback
- **Error Categories**:
  - **TOB File Errors**: Datei nicht gefunden, Format-Fehler, Parsing-Fehler
  - **Database Errors**: Verbindungsfehler, SQL-Fehler, Migration-Fehler
  - **Server Communication Errors**: cURL-Fehler, Timeout, HTTP-Status-Codes
  - **UI Errors**: Widget-Fehler, Plot-Rendering-Fehler, Dialog-Fehler
  - **Validation Errors**: Eingabe-Validierung, Daten-Validierung
- **User Dialog System**:
  - **Error Dialogs**: QMessageBox für kritische Fehler mit Details
  - **Warning Dialogs**: QMessageBox für Warnungen mit Optionen
  - **Info Dialogs**: QMessageBox für informative Nachrichten
  - **Progress Dialogs**: QProgressDialog für lange Operationen
  - **Custom Error Dialogs**: Spezielle Dialoge für komplexe Fehler
- **Error Message Standards**:
  - **Titel**: Kurze, prägnante Beschreibung
  - **Nachricht**: Benutzerfreundliche Erklärung ohne technische Details
  - **Details**: Technische Details in erweiterbarer Sektion
  - **Aktionen**: "OK", "Abbrechen", "Wiederholen", "Details anzeigen"
- **Error Recovery**:
  - **Automatic Retry**: Für temporäre Fehler (Netzwerk, Datei-Zugriff)
  - **Fallback Options**: Alternative Aktionen bei Fehlern
  - **User Guidance**: Hilfetexte und Anleitungen bei Fehlern
- **Error Logging Integration**:
  - **User-visible Errors**: Zusätzlich in Error-Log mit User-ID
  - **Error Context**: Benutzer-Aktion, Zeitstempel, System-Info
  - **Error Tracking**: Eindeutige Error-IDs für Support

### Type Hints (Vollständige Typisierung)
- **Python Version**: 3.13.7 mit vollständiger Type Hint Unterstützung
- **Type Checker**: mypy für statische Typ-Überprüfung
- **Import Standards**: 
  ```python
  from typing import Dict, List, Optional, Union, Tuple, Any
  from pathlib import Path
  import pandas as pd
  ```
- **Funktions-Typisierung**:
  ```python
  def load_tob_file(file_path: Path) -> Tuple[Dict[str, Any], pd.DataFrame]:
  def process_sensor_data(data: pd.DataFrame, sensor_list: List[str]) -> pd.DataFrame:
  ```
- **Klassen-Typisierung**:
  ```python
  class TOBDataModel:
      def __init__(self, file_path: Path) -> None:
      def get_header(self) -> Dict[str, Any]:
      def get_data(self) -> pd.DataFrame:
  ```
- **Optional Types**: Für nullable Werte und Default-Parameter
- **Union Types**: Für verschiedene Datentypen (z.B. str | int)
- **Generic Types**: Für wiederverwendbare Container-Klassen
- **Protocol Types**: Für Duck-Typing und Interface-Definitionen
- **Type Aliases**: Für komplexe Typen (z.B. `SensorData = Dict[str, float]`)

### Internationalisierung (i18n)
- **Standardsprache**: Englisch (en_US)
- **Unterstützte Sprachen**: 
  - Englisch (en_US) - Standard
  - Deutsch (de_DE) - Optional
- **Sprachauswahl**: Über Menübar → Tools → Language (EN/DE)
- **Qt Internationalisierung**:
  - **Qt Linguist**: Für Übersetzungsdateien (.ts/.qm)
  - **tr() Funktionen**: Für alle übersetzbaren Strings
  - **Dynamischer Sprachwechsel**: Ohne Neustart der Anwendung
- **Übersetzungsdateien**:
  - `resources/translations/wizard_en_US.ts` (Englisch - Standard)
  - `resources/translations/wizard_de_DE.ts` (Deutsch)
  - `resources/translations/wizard_en_US.qm` (Kompilierte Englisch-Datei)
  - `resources/translations/wizard_de_DE.qm` (Kompilierte Deutsch-Datei)
- **Übersetzungsbereiche**:
  - **UI-Elemente**: Menüs, Buttons, Labels, Tooltips
  - **Dialoge**: Error-Messages, Info-Dialoge, Projekt-Dialoge
  - **Status-Messages**: Progress-Messages, Status-Updates
  - **Error-Messages**: Benutzerfreundliche Fehlermeldungen
- **Sprach-Persistierung**: 
  - Spracheinstellung wird in User-Settings gespeichert (einzige persistente Einstellung)
  - Automatische Wiederherstellung beim nächsten Start
- **Fallback-Strategie**: Bei fehlenden Übersetzungen → Englisch als Fallback

### Projekt-Verschlüsselung & Sicherheit
- **Verschlüsselungsstandard**: AES-256 (Advanced Encryption Standard)
- **Verschlüsselungsbibliothek**: `cryptography` (Python)
- **Projektdatei-Format**: `.wzp` (Wizard Project - verschlüsselt)
- **Verschlüsselungsstrategie**:
  - **Projekt-Metadaten**: Name, Description, Settings (verschlüsselt)
  - **TOB-Daten**: Komplette .TOB Daten und verarbeitete Sensordaten (verschlüsselt)
  - **Server-Konfiguration**: Keys, URLs, Form-Feld-Namen (verschlüsselt)
  - **Sensitive Data**: Authentifizierung, Server-Kommunikation (verschlüsselt)
- **Schlüssel-Management**:
  - **App-interner Schlüssel**: Konsistenter Schlüssel für alle Projekte
  - **Keine User-Passwörter**: Transparente Verschlüsselung für den User
  - **Key Storage**: Hardcoded im Code (für Entwicklung)
  - **Future**: Key-Derivation oder externe Konfiguration für Production
- **Sicherheitsfeatures**:
  - **Datei-Header**: Magic Bytes zur Identifikation verschlüsselter Dateien
  - **Integrity Check**: HMAC-SHA256 für Datenintegrität
  - **Secure Deletion**: Überschreiben sensibler Daten im Speicher
- **Projekt-Speicherung**:
  - **Lokale Projekte**: Beliebiger Speicherort (.wzp Dateien)
  - **Temporary Files**: Sichere Löschung nach Verwendung
- **Benutzer-Interface**:
  - **Kein Passwort-Dialog**: Transparente Verschlüsselung
  - **Projekt-Bearbeitung**: Edit-Menü für Server-Konfiguration
  - **File Validation**: Automatische .wzp Datei-Erkennung
- **Sicherheitsrichtlinien**:
  - **Keine Klartext-Speicherung**: Alle sensiblen Daten verschlüsselt
  - **Memory Protection**: Sichere Löschung nach Verwendung
  - **File Permissions**: Standard-Dateiberechtigungen
  - **Audit Trail**: Logging von Verschlüsselungs-/Entschlüsselungsvorgängen

### Processing List Dialog (Projektverwaltung)
- **Dialog-Fenster**: Modal Dialog für TOB-Datei-Übersicht
- **Tabellen-Widget**: QTableWidget mit sortierbaren Spalten
- **Spalten-Definition**:
  - **Dateiname**: Name der .TOB Datei
  - **Dateigröße**: Dateigröße in MB/KB
  - **Lade-Datum**: Wann die Datei geladen wurde
  - **Status**: Processing-Status (Loaded, Processed, Sent)
  - **Server-Status**: Status vom Server (Pending, Processing, Completed, Error)
  - **Aktionen**: Buttons für Datei-Aktionen
- **Funktionalitäten**:
  - **Datei anzeigen**: TOB-Datei im Hauptfenster laden und anzeigen
  - **Datei hinzufügen**: Neue .TOB Dateien zum Projekt hinzufügen
  - **Datei entfernen**: TOB-Datei aus Projekt entfernen (mit Bestätigung)
  - **Datei-Details**: Erweiterte Informationen anzeigen
  - **Server-Status abfragen**: Aktuellen Status vom Server abrufen
  - **Plot-Laden**: TOB-Datei direkt im Plot-Frame anzeigen
- **Filter & Sortierung**:
  - **Status-Filter**: Dropdown für Status-Filterung
  - **Datum-Filter**: Von/Bis Datum für Lade-Datum
  - **Größen-Filter**: Min/Max Dateigröße
  - **Spalten-Sortierung**: Klick auf Spalten-Header für Sortierung
- **Kontext-Menü**: Rechtsklick für zusätzliche Aktionen
- **Toolbar-Buttons**:
  - **Add TOB File**: Neue .TOB Datei zum Projekt hinzufügen
  - **Remove Selected**: Ausgewählte Datei(en) entfernen
  - **Load in Plot**: Ausgewählte Datei im Plot-Frame anzeigen
  - **Refresh List**: Liste aktualisieren
  - **Export List**: Liste als CSV exportieren
- **Keyboard Shortcuts**: 
  - **F5**: Liste aktualisieren
  - **Delete**: Ausgewählte Datei entfernen
  - **Enter**: Datei anzeigen
  - **Ctrl+A**: Alle Dateien auswählen
  - **Ctrl+O**: Neue Datei hinzufügen
  - **Ctrl+P**: Datei im Plot laden
- **Drag & Drop**: 
  - **TOB-Dateien**: Drag & Drop von .TOB Dateien in den Dialog
  - **Mehrere Dateien**: Mehrere Dateien gleichzeitig hinzufügen
- **Status-Updates**: Automatische Aktualisierung der Server-Status
- **Error Handling**: Fehlerbehandlung für Server-Kommunikation
- **Bestätigungs-Dialoge**: 
  - **Löschen**: "Sind Sie sicher, dass Sie die ausgewählte(n) Datei(en) entfernen möchten?"
  - **Hinzufügen**: "Datei erfolgreich zum Projekt hinzugefügt"
  - **Plot-Laden**: "Datei wird im Plot-Frame geladen..."

*Hier werden alle wichtigen Entscheidungen und Diskussionen dokumentiert*

---
**Letzte Aktualisierung**: $(date)
**Version**: 1.1
