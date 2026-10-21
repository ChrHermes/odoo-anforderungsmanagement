# Entwicklungsbericht – Anforderungsmanagement

## Ausgangslage, 21.10.2026

Auftrag: MVP M1–M5, Odoo 18 Enterprise, Branch `codex/initial-mvp`. Spezifikationen vollständig gelesen und Wissensbasis vor dem ersten Code initialisiert.

Vorhanden: Python 3.12, Docker, GitHub-Remote und nicht-interaktiver lesender Git-Zugriff. Nicht vorhanden: lokale Odoo-/Helpdesk-Installation, Enterprise-Quellcodezugriff, identifiziertes Odoo.sh-Projekt, bestätigte Deployment-Schutzregeln. GitHub meldet den Development-Branch als ungeschützt.

Eine vorhandene Änderung an `codex-task.md` bleibt unberührt. Es werden keine Kunden-/Produktionsdaten verwendet.

## Fortschritt und Freigabestatus

M1 implementiert: Addon, native Kanban/List/Form/Suche, Gruppen/ACLs, eindeutige unveränderliche Referenz, Pflichtinhalt, Produkthierarchie und 18 geschützte Seed-Datensätze, Archivierung/Löschschutz. Vier Odoo-TransactionCase-Tests im Community-Vertrag bestanden. Zwei Fehler im ersten Testlauf korrigiert (native Rekursionsausnahme und Odoo-assertRaises-Verhalten). Python/XML/Diff-Prüfung erfolgreich. Noch keine Enterprise-Integration und kein echter Upgrade-Durchlauf. M2 folgt. Keine Staging-/Production-Freigabe, keine Deployment-Aktion.

Details und nächste Schritte: `docs/STATUS.md`; technische Entscheidungen: `docs/DECISIONS.md`; Installation und tatsächlich ausgeführte Tests: `docs/RUNBOOK.md`.

## M2 – Workflow und Zusammenarbeit

Implementiert: acht flexible Status, serverseitig neue Begründung bei jeder Zurückstellung/Ablehnung, Historiennotiz, Veröffentlichungsdatum, Statuswizard, interne Followerprüfung einschließlich direkter `mail.followers`-Einträge, interne Notizen und gefilterte Empfänger, manuelle Aktivitäten, 30-Tage-/Aktivitätsfilter. 7 Tests im isolierten Odoo-18-Vertrag erfolgreich (0 Fehler).

Git: M1 `45909f4` erfolgreich nach `origin/codex/initial-mvp` gepusht. Keine anderen Branches verändert. M2 wird separat versioniert. Odoo.sh-Buildstatus mangels Projektzugriff unbekannt.

## M3 – Helpdesk und Vertraulichkeit

Private unveränderliche Ticketquellen, Ticketaktion zum Erstellen/Verknüpfen, eigene Redaktion, n:m-Navigation, Kundenorganisationen und manuelle Beziehungen, autorisierter nicht persistenter Quellenviewer sowie interne Statusnotizen implementiert. Kein öffentliches Relationsfeld auf Snapshotdaten. Aktuelle Ticket-ACLs/Record Rules und Feld-/Read-Beschränkungen werden vor Snapshotausgabe geprüft.

17 Odoo-Tests im synthetischen Vertrag bestanden. Erster M3-Lauf mit 8 Fehlern: erforderliche Beschreibung wurde erst durch DB-Not-Null abgewiesen; jetzt verständliche frühe serverseitige Validierung. Exporttests benötigten zusätzlich die tatsächliche Odoo-Exportgruppe; ergänzt. Wiederholung fehlerfrei. Portal-/Fremdbenutzer, direkte Schnittstellen und Rechteentzug abgedeckt.

M2 `25659e7` erfolgreich gepusht. Keine Enterprise-Installation oder Odoo.sh-Build beobachtet. M3-Enterprise-/Mailgate bleibt offen. M4-Code entsteht unter der ausdrücklichen Offline-Erlaubnis, ohne vorzeitige Freigabe.

## M4 – Duplikate, Zusammenführung und Archivierung

Implementiert: maximal fünf deterministische Vorschläge innerhalb desselben Produkts, bestätigter Merge mit Vorschau und Zeilensperren, unveränderte Originale, fehlende Snapshotkopien einschließlich Capture-Provenienz, manuelle Kundenunion, Originalnavigation und dauerhafte Redirects. Restore behält Redirect. Kein endgültiges Löschen.

21 Tests bestanden. Erster M4-Lauf: zwei Fehlschläge. Einer deckte die Odoo-Standardlöschung offener Aktivitäten beim Archivieren auf; eine eng begrenzte Erhaltung wurde implementiert und die Aktivitätsidentität nach Merge sowie manuelles Abschließen geprüft. Der zweite betraf NewId-Semantik bei ungespeicherten Vorschlägen und wurde im Test korrigiert. M3 `6615c2d` erfolgreich gepusht.
