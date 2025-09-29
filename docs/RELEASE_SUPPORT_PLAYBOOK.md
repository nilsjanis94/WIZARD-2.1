# Release- und Support-Playbook für WIZARD-2.1

Dieses Dokument beschreibt verbindliche Prozesse für Veröffentlichung, Rollback und Support-Betrieb der Desktop-Anwendung WIZARD-2.1. Es ergänzt den Enterprise Readiness Plan und dient als Arbeitsgrundlage für DevOps-, QA- und Support-Teams.

---

## 1. Release-Management

### 1.1 Release-Zyklen und Versionierung
- **Cadence:** Regulatorische Minor-Releases vierteljährlich, Patch-Releases ad-hoc nach Bedarf.
- **Versionierung:** SemVer (`MAJOR.MINOR.PATCH`). Jeder Release-Branch folgt dem Muster `release/vMAJOR.MINOR.x`.
- **Cut-Off:** Feature-Freeze 5 Werktage vor geplantem Go-Live. Nur kritische Fixes nach Freigabe des Release-Managers.

### 1.2 Build- und Artefaktpipeline
1. **Tagging:** Release-Manager erzeugt Git-Tag `vMAJOR.MINOR.PATCH` auf dem freigegebenen Commit.
2. **CI:** Pipeline `release.yml` wird manuell gestartet und umfasst:
   - Dependency-Scan & Lizenzprüfung
   - Linting, Unit-, Integration- und UI-Smoke-Tests
   - Coverage-Check (>=70 %), Abbruch bei Unterschreitung
3. **Artefakt-Erstellung:**
   - macOS `.dmg` via notarisiertem Build
   - Windows `.msi` via `msix`/`wix`-Pipeline (Roadmap)
4. **Code-Signierung:**
   - macOS: Apple Developer ID Zertifikat (KeyChain + Fastlane Notarize)
   - Windows: EV Code Signing Zertifikat (SignTool)
5. **Checksums:** Automatisches Generieren von SHA-256-Hashes. Veröffentlichung gemeinsam mit Release-Notes.

### 1.3 Release Readiness Checklist
| Bereich | Aufgabe | Verantwortlich | Status-Tracking |
|---------|---------|----------------|-----------------|
| QA | Regression + UI-Smoke-Test abgeschlossen | QA Lead | TestRail / Jira |
| Security | Dependency Audit (SCA), Secrets-Scan | Security Engineer | GitHub Advanced Security |
| Ops | Monitoring-Konfiguration geprüft | DevOps | Grafana Dashboard |
| Support | Release-Notes final, FAQ aktualisiert | Support Lead | Confluence |
| Management | Go-Live-Freigabe dokumentiert | Product Owner | Jira Ticket |

### 1.4 Rollout-Strategie
- **Staging:** Veröffentlichung in internen Update-Kanal; Pilotanwender (5 %) testen 48h.
- **Production:** Stepwise Rollout (25 % → 50 % → 100 %) via Auto-Updater.
- **Kommunikation:** Release-Notes + Änderungsdokument in Kundenportal, Statusmeldung im internen Slack-Channel `#wizard-release`.

---

## 2. Rollback-Strategie

### 2.1 Entscheidungs-Matrix
| Kriterium | Beispiel | Aktion |
|-----------|----------|--------|
| Kritische Ausfälle (Datenverlust, Startverhinderung) | Crash bei Projektöffnung | Sofortiger Rollback |
| Hoher Impact, Workaround verfügbar | Fehlende UI-Funktion, aber CLI nutzbar | Hotfix innerhalb 24h |
| Niedriger Impact | Tippfehler, UI-Glitch | Fix im nächsten Patch |

### 2.2 Rollback-Prozess
1. **Incident-Entscheid:** On-Call DevOps bewertet Crash/Support-Tickets gemeinsam mit Product Owner.
2. **Rollback-Bestand:**
   - Auto-Updater verweist auf vorheriges signiertes Artefakt (`latest-stable.json`).
   - S3/Blob Storage behält die letzten **3** Releases mit Checksums.
3. **Rollback-Operation:**
   - Update-Feed auf vorherige Version umstellen
   - Notarize/Signatur bereits vorhanden -> keine erneute Signierung notwendig
4. **Kommunikation:** Kanäle wie bei Rollout, aber mit Hinweis auf Rücknahme und nächsten Fix-Termin.
5. **Post-Mortem:** Innerhalb von 3 Arbeitstagen schriftliches Review (Root Cause, Guardrails) im Incident-Log.

### 2.3 Datenmigration & Kompatibilität
- Migrationsskripte müssen rückwärts kompatibel sein (Down-Migrations). 
- Projektdateien `.wzp` behalten Schema-Version; bei Downgrade prüft App auf ältere Runtime, bietet Read-Only-Mode mit Export an.

---

## 3. Crash- und Fehler-Reporting

### 3.1 Tools & Infrastruktur
- **Crash-Reporter:** Sentry (macOS) / Windows Error Reporting + Sentry Wrapper
- **Log-Kanäle:**
  - `wizard_app.log` (Allgemein)
  - `wizard_error.log` (Error-Level)
  - `wizard_audit.log` (Security & Compliance)
- **Upload:**
  - Crash-Dumps verschlüsselt (`AES-256`) und asynchron via HTTPS an Monitoring-Backend
  - Logrotate täglich, 30 Tage Aufbewahrung (audit: 180 Tage)

### 3.2 Schwellenwerte & Alerts
| Kategorie | Schwelle | Aktion |
|-----------|----------|--------|
| Crashrate | >2 % aktive Clients | On-Call PagerDuty, Rollback-Entscheid |
| Fehlermeldung `TOB_PARSE_ERROR` | >10 Ereignisse/24h | QA Analyse, Hotfix planen |
| Memory Warning | 90 % eines Hosts | Support informiert Kunden, Workaround dokumentieren |

### 3.3 Support-Workflow
1. **Ticket-Erfassung:** Zendesk → Priorisierung nach SLA (Critical 4h, High 8h, Normal 24h)
2. **Analyse:** Support nutzt Crash-ID / Logfiles + Knowledge Base
3. **Eskalation:** Bei reproduzierbaren Bugs → Jira Issue (Label `production-incident`)
4. **Kommunikation:** Status-Updates über Ticket-System; bei Major Incidents zusätzlich Kunden-Rundmail
5. **Abschluss:** Ticket nur schließen, wenn Ursache/Workaround dokumentiert + Kunde bestätigt

---

## 4. Deployment-Backlog & Automatisierung

| Task | Ziel | Status |
|------|------|--------|
| GitHub Actions `release.yml` finalisieren (Build, Tests, Signing) | Consistent release pipeline | open |
| Auto-Updater für Windows integrieren (MSIX/Chocolatey) | Parität macOS ↔ Windows | planned |
| Sentry Crash-Reporting in Desktop-App aktivieren | Vollständige Fehlertransparenz | in progress |
| Rollback-Skript (Feed Switch + Notification) | Geschwindigkeit im Incident-Fall | planned |
| Support-FAQ + Known-Issues-DB | Wissenstransfer | open |

---

## 5. Verantwortlichkeiten

- **Release Manager (DevOps Lead):** Koordination Pipeline, Artefakt-Signierung, Rollout-Freigabe
- **QA Lead:** Abschlussberichte, Coverage-Check, Abnahmeprotokoll
- **Security Engineer:** Zertifikatsverwaltung, Audit-Log-Kontrolle
- **Support Lead:** Kommunikationsplan, Ticket-Handling, FAQ-Pflege
- **Product Owner:** Go-/No-Go-Entscheid, Priorisierung von Hotfixes

Backup-Verantwortlichkeiten sind in der Team-Matrix (Confluence) hinterlegt.

---

## 6. Artefakt- und Dokumentations-Ablage

| Artefakt | Ablageort | Retention |
|----------|-----------|-----------|
| Signierte Binaries (`.dmg`, `.msi`) | S3 Bucket `wizard-release` | 12 Monate |
| Release-Notes | Confluence > WIZARD Knowledge Base | unbegrenzt |
| Checksums + SBOM | GitHub Release Assets | 12 Monate |
| Incident Reports & Post-Mortems | Notion Incident Hub | unbegrenzt |

Dokument-Revisionen werden über Git versioniert und halbjährlich überprüft.

---

## 7. Offene Punkte / Roadmap
- Automatisiertes User Acceptance Testing (UAT) in Pilotkunden-Umgebung
- Integration von Rollout-Telemetrie in zentralem Dashboard (Grafana)
- Einrichtung von Chaos-Tests für Failover-Szenarien
- Konsolidiertes Onboarding-Paket für Support-Mitarbeitende (Checklisten + Schulungsunterlagen)

---

**Stand:** September 2025 – Verantwortliche Teams aktualisieren dieses Dokument nach jedem Release-Zyklus.
