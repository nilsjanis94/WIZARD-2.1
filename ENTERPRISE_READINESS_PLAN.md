# WIZARD-2.1 Enterprise Readiness Plan

Dieser Leitfaden dokumentiert die aktuellen Lücken im Vergleich zu einem üblichen Unternehmensstandard und definiert konkrete Arbeitspakete. Er dient als Referenz für weitere Planungsschritte.

## 1. Sicherheitsarchitektur

- **Lücken**
  - Keine Authentifizierung/Autorisierung für Benutzer- oder Servicezugriffe.
  - App-interner statischer AES-Schlüssel statt nachhaltigem Secrets-Management.
  - Kein Audit-Logging und keine Richtlinien für Log-Aufbewahrung/Datenschutz.
  - Fehlende Bedrohungsanalyse und Sicherheitsrichtlinien (z. B. Härtung, Patch-Management).
- **Maßnahmen**
  - Sicherheitskonzept (IAM-Strategie, Rollenmodell, Rechteverwaltung) erarbeiten und implementieren.
  - Secrets-Management etablieren (z. B. OS Keychain, Vault) und Schlüsselrotation festlegen.
  - Audit-Logging definieren (Log-Inhalte, Aufbewahrung, Zugriffsschutz) und technisch umsetzen.
  - Security-Policies dokumentieren inkl. verpflichtender Code- und Dependency-Scans.

## 2. Qualitäts- & Teststrategie

- **Lücken**
  - Testabdeckung (~30 %) unter Enterprise-Niveau; kritische Schichten (Controller/UI) ungetestet.
  - Kein End-to-End-Testing, keine Last- und Performance-Tests.
  - Fehlendes Test-Reporting (Dashboards, Trendanalysen).
- **Maßnahmen**
  - Testplan definieren (Scope, Metriken, Abnahme-Kriterien) und Coverage-Ziel >70 % festschreiben.
  - Automatisierte Tests für kritische Services und UI-Smoketests implementieren.
  - CI-Pipeline verpflichtend mit Tests, Coverage-Check und Quality-Gates ausführen.

## 3. Betriebsprozesse & Support

- **Lücken**
  - Keine dokumentierten Release-/Deployment-Prozesse inkl. Rollback.
  - Fehlendes Monitoring (Health-Checks, Crash-Reports) und Incident-Response.
  - Update-Mechanismus nur auf Konzept-Level; keine automatisierten Releases.
- **Maßnahmen**
  - Betriebskonzept erstellen (Release-Zyklen, Freigabe-Checklisten, Rollback-Strategie).
  - Crash-/Fehler-Reporting etablieren und Support-Workflow dokumentieren.
  - Automatisierte Build-/Release-Pipeline (Signierung, Artefakt-Distribution) finalisieren.

## 4. Compliance & Governance

- **Lücken**
  - Rollen & Berechtigungen im Projektkontext nicht festgelegt.
  - Keine Richtlinien zu Datenschutz, Datenklassifizierung oder Archivierung.
  - Fehlendes Risiko- und Compliance-Register.
- **Maßnahmen**
  - Verantwortlichkeiten (RACI) und Change-Management-Prozess abstimmen.
  - Datenschutz- und Archivierungsrichtlinien festlegen (inkl. Data Retention, Zugriffskontrolle).
  - Risiko- und Compliance-Matrix erstellen und regelmäßig aktualisieren.

## 5. Dokumentation & Wissensmanagement

- **Lücken**
  - Sicherheits-, Betriebs- und Support-Handbücher fehlen.
  - Kein dokumentierter Onboarding-Prozess für neue Teammitglieder.
  - Architekturentscheidungen (ADR) nur teilweise erfasst.
- **Maßnahmen**
  - Handbücher für Security, Ops, Support und QA erstellen.
  - Onboarding-Guide mit Entwicklungs- und Qualitätsstandards erarbeiten.
  - Architekturentscheidungen fortlaufend in ADRs dokumentieren.

## 6. Roadmap & Priorisierung

| Priorität | Arbeitspaket | Zieltermin | Verantwortlich |
|-----------|--------------|------------|----------------|
| Hoch | Sicherheitskonzept (IAM, Secrets, Audit) | tbd | tbd |
| Hoch | Teststrategie erweitern (UI/E2E, Coverage) | tbd | tbd |
| Mittel | Betriebs- und Release-Prozess dokumentieren | tbd | tbd |
| Mittel | Monitoring & Incident-Response etablieren | tbd | tbd |
| Niedrig | Governance-/Compliance-Dokumente finalisieren | tbd | tbd |

> **Hinweis:** Termin- und Verantwortlich-Spalten bewusst offen lassen und gemeinsam festlegen.

## 7. Nächste Schritte (Kurzfristiger Fokus)

1. Kick-off-Workshop zur Sicherheitsarchitektur organisieren, Verantwortlichkeiten festlegen.
2. Teststrategie-Workshop durchführen und konkrete Sprint-Ziele ableiten (z. B. UI-Smoke-Test, Coverage-Anhebung).
3. Blueprint für Release- und Support-Prozesse entwerfen, Feedback der Stakeholder einholen.
4. Dokumentations-Backlog pflegen und in den Projektplan integrieren.

---

*Stand: September 2025 – Dokument wird fortlaufend aktualisiert.*


