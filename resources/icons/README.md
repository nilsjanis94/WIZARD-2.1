# WIZARD-2.1 Icons

Dieser Ordner enthält die Icon-Dateien für die WIZARD-2.1 Anwendung.

## Verwendung

### plot_logo_label Icon
- **Dateiname:** `wizardLogo_transparent.png`
- **Größe:** Wird auf 32x32 Pixel skaliert (scaledContents=true)
- **Format:** PNG mit Transparenz
- **Verwendung:** Wird im plot_info_container oben rechts angezeigt
- **Quelle:** FIELAX Logo mit transparentem Hintergrund

## Icon-Standards

- **Format:** PNG mit Transparenz
- **Größe:** 32x32 Pixel für kleine Icons, 64x64 für größere
- **Farbe:** Sollte zum FIELAX Branding passen
- **Qualität:** Hochauflösende Grafiken bevorzugt

## Hinzufügen neuer Icons

1. Icon-Datei in diesen Ordner legen
2. In der `ui/main_window.ui` Datei das entsprechende Label konfigurieren:
   ```xml
   <property name="pixmap">
     <pixmap>resources/icons/[icon_name].png</pixmap>
   </property>
   <property name="scaledContents">
     <bool>true</bool>
   </property>
   ```

## FIELAX Branding

Das Logo sollte die FIELAX Farben und das Design verwenden:
- **Primärfarbe:** #3AAA35 (Grün)
- **Sekundärfarbe:** Weiß für Kontrast
- **Stil:** Professionell, wissenschaftlich, vertrauenswürdig
