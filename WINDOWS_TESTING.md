# WIZARD-2.1 - Windows Testing Guide

Dieser Leitfaden erklärt, wie du die WIZARD-2.1 Anwendung auf Windows testen kannst, wenn du auf einem MacBook entwickelst.

## Übersicht der Test-Methoden

### 1. GitHub Actions (Empfohlen für kontinuierliche Integration)

Die Anwendung wird automatisch auf Windows, macOS und Linux getestet, wenn du Code pusht.

**Einrichtung:**
1. Push dein Projekt zu GitHub
2. Die `.github/workflows/ci.yml` Pipeline testet automatisch auf allen Plattformen
3. Ergebnisse siehst du im "Actions" Tab deines Repositories

### 2. Lokale Virtualisierung (Für intensive UI-Tests)

**Option A: Parallels Desktop (Mac nativ)**
```bash
# Auf deinem MacBook:
# 1. Parallels Desktop installieren
# 2. Windows 11 VM erstellen
# 3. VM starten und Windows einrichten
```

**Option B: UTM (Kostenlos, Open-Source)**
```bash
# UTM kann Windows VMs auf Apple Silicon laufen lassen
brew install utm
```

**Option C: VirtualBox**
```bash
brew install virtualbox
# Windows ISO herunterladen und VM erstellen
```

### 3. Cloud VMs (Für schnelle Tests)

**Azure Virtual Machines:**
- Kostenlose Test-Credits verfügbar
- Windows Server oder Windows 11 VMs
- RDP für Remote-Desktop Zugriff

**AWS EC2:**
- Windows Server AMIs verfügbar
- Pay-as-you-go Pricing

### 4. Windows PowerShell Script (Automatisiert)

Das bereitgestellte `scripts/test_windows.ps1` Script automatisiert den gesamten Test-Prozess:

```powershell
# Auf Windows VM/Powershell:
.\scripts\test_windows.ps1          # Vollständiger Test
.\scripts\test_windows.ps1 -Clean   # Mit Cleanup
.\scripts\test_windows.ps1 -SkipTests # Nur Setup
```

## Schritt-für-Schritt Anleitung

### Vorbereitung auf dem MacBook

1. **Projekt pushen:**
```bash
git add .
git commit -m "Add Windows testing support"
git push origin main
```

2. **GitHub Actions beobachten:**
- Gehe zu deinem GitHub Repository
- Klicke auf "Actions"
- Sieh dir die Windows-Test-Ergebnisse an

### Windows VM Setup

1. **Windows 11 VM erstellen** (empfohlen für moderne Qt-Apps)

2. **Python installieren:**
```powershell
# Windows PowerShell als Administrator
winget install Python.Python.3.13
```

3. **Projekt klonen:**
```bash
git clone https://github.com/YOUR_USERNAME/wizard-2.1.git
cd wizard-2.1
```

4. **Automatisiertes Setup:**
```powershell
# PowerShell im Projekt-Verzeichnis
.\scripts\test_windows.ps1
```

## Wichtige Cross-Platform Überlegungen

### Qt-spezifische Unterschiede

**Schriftarten:**
- Windows verwendet andere Standardschriftarten als macOS
- Arial ist auf allen Plattformen verfügbar
- Unsere plattformspezifische Schriftart-Erkennung sorgt für Kompatibilität

**UI-Themes:**
- Windows verwendet andere Standard-Window-Dekorationen
- Qt's "Fusion" Style sorgt für konsistente Darstellung
- Unsere expliziten Schriftfarben funktionieren plattformübergreifend

**Datei-Dialoge:**
- Windows verwendet native Explorer-Dialoge
- Pfad-Separatoren: `\` auf Windows vs `/` auf macOS
- Unsere Pfad-Behandlung ist bereits cross-platform

### Bekannte Windows-spezifische Probleme

1. **Qt6 WebEngine Abhängigkeiten:**
   - Stelle sicher, dass alle Qt6-Komponenten installiert sind
   - `PyQt6-Qt6` Paket enthält alle nötigen DLLs

2. **Antivirus-Software:**
   - Windows Defender kann PyQt-Apps blockieren
   - Füge Ausnahmen für das Projekt-Verzeichnis hinzu

3. **Display-Scaling:**
   - Windows High-DPI-Support kann anders funktionieren
   - Qt skaliert automatisch, aber teste auf verschiedenen DPI-Einstellungen

## Test-Checkliste für Windows

### Automatische Tests
- [ ] `scripts/test_windows.ps1` läuft ohne Fehler
- [ ] PyQt6 importiert erfolgreich
- [ ] UI-Service erkennt Windows-Plattform korrekt
- [ ] pytest Tests bestehen

### Manuelle UI-Tests
- [ ] Anwendung startet ohne Fehler
- [ ] Alle Schriftarten sind schwarz und lesbar
- [ ] Comboboxen funktionieren (Dropdown, Text sichtbar)
- [ ] Buttons und Labels sind lesbar
- [ ] Plot-Bereich rendert korrekt

### Funktionale Tests
- [ ] .tob Dateien können geöffnet werden
- [ ] Achsen-Controls funktionieren
- [ ] Plot-Updates arbeiten
- [ ] Projekt-Speicherung/Laden funktioniert

## Troubleshooting

### Häufige Probleme

**"ModuleNotFoundError: No module named 'PyQt6'"**
```powershell
pip install PyQt6 PyQt6-Qt6
# Oder für 64-bit Windows:
pip install PyQt6 --only-binary all
```

**Qt Platform Plugin Fehler:**
```powershell
# Setze Umgebungsvariable für Qt
$env:QT_QPA_PLATFORM = "windows"
```

**Schriftfarben nicht sichtbar:**
- Unsere plattformspezifischen Fixes sollten das beheben
- Prüfe Windows Theme-Einstellungen (Hell/Dunkel-Modus)

**Performance-Probleme in VM:**
- Erhöhe RAM für VM (mindestens 4GB)
- Aktiviere Hardware-Beschleunigung in VM-Settings

## CI/CD Pipeline Details

Die `.github/workflows/ci.yml` führt folgende Tests auf Windows durch:

1. **Python 3.13 Setup**
2. **Dependency Installation**
3. **Unit Tests mit pytest**
4. **Coverage Reporting**
5. **Cross-platform Kompatibilität**

## Ressourcen

- [Qt for Windows Documentation](https://doc.qt.io/qt-6/windows.html)
- [PyQt6 Windows Installation](https://www.riverbankcomputing.com/software/pyqt6/download)
- [Windows Development Environment Setup](https://docs.microsoft.com/en-us/windows/dev-environment/)

## Support

Bei Problemen:
1. Prüfe die GitHub Actions Logs
2. Schaue in `logs/wizard_error.log` auf der Windows-VM
3. Vergleiche mit macOS-Verhalten
4. Erstelle ein Issue mit detaillierten Logs
