# Entwicklungsbericht – Anforderungsmanagement

## Ausgangslage, 21.10.2026

Auftrag: MVP M1–M5, Odoo 18 Enterprise, Branch `codex/initial-mvp`. Spezifikationen vollständig gelesen und Wissensbasis vor dem ersten Code initialisiert.

Vorhanden: Python 3.12, Docker, GitHub-Remote und nicht-interaktiver lesender Git-Zugriff. Nicht vorhanden: lokale Odoo-/Helpdesk-Installation, Enterprise-Quellcodezugriff, identifiziertes Odoo.sh-Projekt, bestätigte Deployment-Schutzregeln. GitHub meldet den Development-Branch als ungeschützt.

Eine vorhandene Änderung an `codex-task.md` bleibt unberührt. Es werden keine Kunden-/Produktionsdaten verwendet.

## Fortschritt und Freigabestatus

M1 implementiert: Addon, native Kanban/List/Form/Suche, Gruppen/ACLs, eindeutige unveränderliche Referenz, Pflichtinhalt, Produkthierarchie und 18 geschützte Seed-Datensätze, Archivierung/Löschschutz. Vier Odoo-TransactionCase-Tests im Community-Vertrag bestanden. Zwei Fehler im ersten Testlauf korrigiert (native Rekursionsausnahme und Odoo-assertRaises-Verhalten). Python/XML/Diff-Prüfung erfolgreich. Noch keine Enterprise-Integration und kein echter Upgrade-Durchlauf. M2 folgt. Keine Staging-/Production-Freigabe, keine Deployment-Aktion.

Details und nächste Schritte: `docs/STATUS.md`; technische Entscheidungen: `docs/DECISIONS.md`; Installation und tatsächlich ausgeführte Tests: `docs/RUNBOOK.md`.
