# Governance & Compliance Guide für WIZARD-2.1

Dieses Dokument definiert zentrale Governance-Strukturen für das WIZARD-2.1 Projekt. Es bildet die Basis für Verantwortlichkeiten, Datenschutz- und Archivierungsrichtlinien sowie das Risiko- und Compliance-Management.

---

## 1. Organisations- und Rollenmodell

### 1.1 Kernrollen
| Rolle | Hauptverantwortung | Stellvertretung |
|-------|--------------------|-----------------|
| Product Owner | Priorisierung, Release-Freigaben, Stakeholder-Kommunikation | Business Analyst |
| Tech Lead | Architekturentscheidungen, Code-Standards, Security-Gatekeeper | Senior Developer |
| QA Lead | Teststrategie, Coverage-Monitoring, QA-Reporting | QA Engineer |
| DevOps Lead | CI/CD, Infrastruktur, Deployment, Monitoring | DevOps Engineer |
| Security Officer | Bedrohungsmodelle, Audits, Secrets & Logging | Tech Lead |
| Compliance Manager | Policies, Data Retention, Audit Trails | Product Owner |
| Support Lead | Kundenkommunikation, Incident-Eskalation | Support Engineer |

### 1.2 Governance-Gremien
- **Steering Committee (monatlich):** Product Owner, Tech Lead, Security Officer, DevOps Lead
  - Themen: Roadmap, Risikobewertung, Compliance-Reviews
- **Security & Privacy Guild (vierteljährlich):** Security Officer, Tech Lead, Compliance Manager
  - Themen: Threat Modeling, Richtlinien-Updates, Datenschutz-Audits
- **Release Board (pro Release):** Product Owner, QA Lead, DevOps Lead
  - Themen: Go/No-Go, Rollout-Plan, Incident-Bereitschaft

---

## 2. RACI-Matrix

| Deliverable / Prozess | Product Owner | Tech Lead | QA Lead | DevOps Lead | Security Officer | Compliance Manager | Support Lead |
|-----------------------|---------------|-----------|---------|-------------|------------------|--------------------|--------------|
| Produkt-Roadmap | R | C | C | I | I | I | I |
| Architekturentscheidungen (ADR) | C | R | I | I | C | I | I |
| Sicherheitskonzept (IAM, Secrets, Audit) | A | C | I | I | R | C | I |
| Teststrategie & Coverage | C | I | R | I | I | I | I |
| CI/CD Pipeline & Releaseverfahren | I | C | A | R | I | I | I |
| Datenschutz-Richtlinien | C | I | I | I | C | R | I |
| Datenarchivierung & Retention | C | I | I | I | C | R | I |
| Incident Response / Rollback | I | C | I | R | C | I | A |
| Customer Support Playbooks | I | I | I | I | I | C | R |

Legende: **R** = Responsible, **A** = Accountable, **C** = Consulted, **I** = Informed.

---

## 3. Datenschutz- und Archivierungsrichtlinien

### 3.1 Datenklassifizierung
| Kategorie | Beschreibung | Schutzbedarf |
|-----------|--------------|--------------|
| **Öffentlich** | Marketingmaterial, Release-Notes | Niedrig |
| **Intern** | technische Dokumentation, Logs ohne PII | Mittel |
| **Vertraulich** | Kundendaten, Crash-Dumps mit PII, Audit-Logs | Hoch |
| **Streng Vertraulich** | Kryptographische Schlüssel, Credentials | Sehr Hoch |

### 3.2 Richtlinien
- **Datenerhebung:** Crash-Dumps werden standardmäßig **anonymisiert** (Session-ID statt Benutzername). Opt-Out im Client möglich.
- **Speicherung:**
  - Audit-Logs: 180 Tage (verschlüsselt, Zugriff nur Security Officer & Compliance Manager)
  - Crash-Reports: 90 Tage (Produkt-/Support-Team auf Anfrage)
  - Support-Tickets: 365 Tage (Retention durch Ticket-System)
- **Zugriffskontrolle:**
  - Role-Based Access Control (RBAC) via Azure AD/Okta
  - Geheimdaten nur über Secrets Management (Keychain/Vault) verfügbar
- **Archivierung:**
  - Monatlicher Export kritischer Logs (Audit/Ausnahmen) nach S3 Glacier Vault
  - Halbjährliche Archivprüfung und Löschung nach Retention-Plan
- **Verfahren bei DSGVO-Anfragen:**
  - Daten-Auskunft binnen 30 Tagen (Owner: Compliance Manager)
  - Löschanforderungen in Crash-/Support-Daten => Ticket zur forensischen Verifikation, danach redaktionelle Datenbereinigung

### 3.3 Dokumentierte Verfahren
1. **Data Inventory:** Verzeichnis aller Datenflüsse (Input → Verarbeitung → Output) mit Verantwortlichen.
2. **Privacy Impact Assessment (PIA):** Bei neuen Features mit personenbezogener Datennutzung verpflichtend.
3. **Datenleck-Management:** SOP mit Eskalationsmatrix (Security Officer → Compliance Manager → Geschäftsführung), 72h-Meldepflicht berücksichtigen.

---

## 4. Risiko- und Compliance-Management

### 4.1 Risikoregister (Kurzform)
| ID | Risiko | Auswirkung | Wahrscheinlichkeit | Score | Gegenmaßnahmen | Verantwortlich |
|----|--------|------------|--------------------|-------|-----------------|----------------|
| R1 | Unsichere Speicherung von Secrets | Datenkompromittierung | Mittel | 12 | Secrets Manager + Key Rotation | Security Officer |
| R2 | Unzureichende Testabdeckung | Release-Regression | Hoch | 16 | Teststrategie 70% Coverage + QA-Gates | QA Lead |
| R3 | Fehlender Rollback-Prozess | Längere Downtime | Mittel | 9 | Implementiertes Rollback-Playbook, Übungen | DevOps Lead |
| R4 | Datenschutzverletzung Crash-Dumps | DSGVO-Strafen | Niedrig | 8 | Pseudonymisierung, Retention Policies | Compliance Manager |
| R5 | Fehlende Incident-Kommunikation | Reputationsschaden | Mittel | 12 | Support-Runbooks, Kommunikationsplan | Support Lead |

Score = Impact (1-5) * Likelihood (1-5).

### 4.2 Risiko-Workflow
1. **Identifikation:** Jede/r Mitarbeitende kann Risiken im Jira-Board `RISK` anlegen.
2. **Bewertung:** Steering Committee (monatlich) prüft Score, entscheidet über Maßnahmen.
3. **Behandlung:** Maßnahmenplan + Owner + Termin werden im Register gepflegt.
4. **Monitoring:** Quartalsweise Review + Update des Registers.
5. **Reporting:** Zusammenfassung in Steering-Committee-Protokoll + Management-Report.

### 4.3 Compliance-Checks
- **Quartals-Checks** (Security Officer & Compliance Manager):
  - Richtlinien-Review (Datenschutz, Archivierung, Zugriffskontrollen)
  - Audit der Secrets-Manager (Zugriffe, Rotation)
  - Stichprobe von Support-Tickets auf SLA-Einhaltung
- **Jährliche Audits**:
  - Externer Penetrationstest (Security Officer organisiert)
  - Datenschutz-Audit gegen DSGVO-Art. 30, 32
  - Lizenz-Compliance (Abgleich Third-Party Libraries mit SBOM)

---

## 5. Change-Management-Prozess

1. **Antrag (RFC):** Jede signifikante Änderung (Feature, Infrastruktur, Policy) erfordert ein schriftliches RFC (Jira Template `RFC`).
2. **Bewertung:** Tech Lead + Product Owner + Security Officer reviewen Impact & Risiken.
3. **Genehmigung:** Freigabe durch Steering Committee oder Release Board.
4. **Implementierung:** Feature Branch, Tests, Dokumentation aktualisieren.
5. **Kommunikation:** Release Notes, Update in Knowledge Base, Schulungen falls nötig.
6. **Nachverfolgung:** Post-Implementation Review (PIR) nach 1 Sprint.

Rollout/Außerplanmäßige Änderungen folgen dem Playbook im `Change Management SOP` (Confluence-Verweis).

---

## 6. Dokumentations- und Wissensmanagement
- **Ablage:** Confluence (Policies, SOPs), Git (ADR, Playbooks), SharePoint (Audit-Reports).
- **Onboarding:** Jede neue Rolle erhält Zugriff auf:
  - Governance Guide (dieses Dokument)
  - Release & Support Playbook
  - Security & QA Checklisten
- **Aktualisierungspflicht:**
  - Tech Lead & Security Officer: mind. halbjährliche Review",
