# Entwicklungsbericht – Anforderungsmanagement

## Ergänzungsauftrag, 22.10.2026

Name **Anforderungen**, Modul `gc_requirements` unverändert, Version `18.0.1.1.0`. Deutsche Labels/Katalog und ein Locale-Test ergänzen alle bisherigen Tests. Frischer Odoo-18-Vertragsinstall 27/27, alter Git-Kandidat 26/26, anschließendes Modulupgrade 27/27; erweiterte Inventur samt negativen Korruptionsproben bestanden. Statische Prüfung, Ruff und Formatprüfung erfolgreich. Vollständige Enterprise-Abnahme und 18->20-Datenmigration weiterhin offen. Odoo-20-Portierung separat vorgesehen; [aktuelle Versionsmatrix und Migrationsweg](docs/COMPATIBILITY.md).

Vorhandene Nutzeränderungen einschließlich CRLF-Konvertierungen, gelöschter `codex-task.md` und neuer `tasks/` bleiben unberührt und aus den Commits ausgeschlossen.

## Historischer MVP-Kandidat, 21.10.2026

**M1–M5-Code im verfügbaren Offline-Umfang implementiert; Enterprise-/Odoo.sh-/visuelle-/Staging-Abnahme offen.** Keine Production-Freigabe. Vollständige fachliche Zuordnung: `docs/ACCEPTANCE.md`.

Finaler lokaler Nachweis mit `python3 scripts/test_contract.py`: Odoo Community **18.0-20261015**, synthetischer Helpdesk-Vertrag, frische Installation **26 Tests bestanden**, tatsächliches Upgrade **26 Tests bestanden**, jeweils 0 Fehler. Geänderte Seeds, bestehende REQ-Nummer, unveränderliche Quelle und physischer Filestore-Anhang überleben das Upgrade. 1.000 Anforderungen/2.000 unterschiedlichen Tickets und Quellen: 13 SQL-Abfragen für die aggregierten Zähler bei kaltem Cache. Statische Paket-/Syntax-/XML-Prüfung, Ruff und Formatprüfung erfolgreich. Keine lizenzierten Enterprise-Integrationstests daraus ableiten.

Repository enthält native Anwendung, automatisierte Tests, reproduzierbare Docker-Testumgebung, GitHub-Vertragsworkflow, Changelog, Installations-/Testanleitung und versionierte Wissensbasis. Alle durch diese Entwicklung angelegten synthetischen Teststacks wurden beendet/entfernt; heruntergeladene Images bleiben als Testcache erhalten. Vorhandene Nutzeränderung `codex-task.md` bleibt unberührt.

## Ausgangslage, 21.10.2026

Auftrag: MVP M1–M5, Odoo 18 Enterprise, Branch `codex/initial-mvp`. Spezifikationen vollständig gelesen und Wissensbasis vor dem ersten Code initialisiert.

Vorhanden: Python 3.12, Docker, GitHub-Remote und nicht-interaktiver lesender Git-Zugriff. Nicht vorhanden: lokale Odoo-/Helpdesk-Installation, Enterprise-Quellcodezugriff, identifiziertes Odoo.sh-Projekt, bestätigte Deployment-Schutzregeln. GitHub meldet den Development-Branch als ungeschützt.

Eine vorhandene Änderung an `codex-task.md` bleibt unberührt. Es werden keine Kunden-/Produktionsdaten verwendet.

## Fortschritt und Freigabestatus

M1 implementiert: Addon, native Kanban/List/Form/Suche, Gruppen/ACLs, eindeutige unveränderliche Referenz, Pflichtinhalt, Produkthierarchie und 18 geschützte Seed-Datensätze, Archivierung/Löschschutz. Zunächst vier Odoo-TransactionCase-Tests im Community-Vertrag bestanden. Zwei Fehler im ersten Testlauf korrigiert (native Rekursionsausnahme und Odoo-assertRaises-Verhalten). Python/XML/Diff-Prüfung erfolgreich. Weitere Meilensteine und Upgrade-Nachweise folgen unten. Keine Staging-/Production-Freigabe.

Details und nächste Schritte: `docs/STATUS.md`; technische Entscheidungen: `docs/DECISIONS.md`; Installation und tatsächlich ausgeführte Tests: `docs/RUNBOOK.md`.

## M2 – Workflow und Zusammenarbeit

Implementiert: acht flexible Status, serverseitig neue Begründung bei jeder Zurückstellung/Ablehnung, Historiennotiz, Veröffentlichungsdatum, Statuswizard, interne Followerprüfung einschließlich direkter `mail.followers`-Einträge, interne Notizen und gefilterte Empfänger, manuelle Aktivitäten, 30-Tage-/Aktivitätsfilter. 7 Tests im isolierten Odoo-18-Vertrag erfolgreich (0 Fehler).

Git: M1 `45909f4` und M2 `25659e7` erfolgreich nach `origin/codex/initial-mvp` gepusht. Keine anderen Branches verändert. Odoo.sh-Buildstatus mangels Projektzugriff unbekannt.

## M3 – Helpdesk und Vertraulichkeit

Private unveränderliche Ticketquellen, Ticketaktion zum Erstellen/Verknüpfen, eigene Redaktion, n:m-Navigation, Kundenorganisationen und manuelle Beziehungen, autorisierter nicht persistenter Quellenviewer sowie interne Statusnotizen implementiert. Kein öffentliches Relationsfeld auf Snapshotdaten. Aktuelle Ticket-ACLs/Record Rules und Feld-/Read-Beschränkungen werden vor Snapshotausgabe geprüft.

17 Odoo-Tests im synthetischen Vertrag bestanden. Erster M3-Lauf mit 8 Fehlern: erforderliche Beschreibung wurde erst durch DB-Not-Null abgewiesen; jetzt verständliche frühe serverseitige Validierung. Exporttests benötigten zusätzlich die tatsächliche Odoo-Exportgruppe; ergänzt. Wiederholung fehlerfrei. Portal-/Fremdbenutzer, direkte Schnittstellen und Rechteentzug abgedeckt.

M2 `25659e7` erfolgreich gepusht. Keine Enterprise-Installation oder Odoo.sh-Build beobachtet. M3-Enterprise-/Mailgate bleibt offen. M4-Code entsteht unter der ausdrücklichen Offline-Erlaubnis, ohne vorzeitige Freigabe.

## M4 – Duplikate, Zusammenführung und Archivierung

Implementiert: maximal fünf deterministische Vorschläge innerhalb desselben Produkts, bestätigter Merge mit Vorschau und Zeilensperren, unveränderte Originale, fehlende Snapshotkopien einschließlich Capture-Provenienz, manuelle Kundenunion, Originalnavigation und dauerhafte Redirects. Restore behält Redirect. Kein endgültiges Löschen.

21 Tests bestanden. Erster M4-Lauf: zwei Fehlschläge. Einer deckte die Odoo-Standardlöschung offener Aktivitäten beim Archivieren auf; eine eng begrenzte Erhaltung wurde implementiert und die Aktivitätsidentität nach Merge sowie manuelles Abschließen geprüft. Der zweite betraf NewId-Semantik bei ungespeicherten Vorschlägen und wurde im Test korrigiert. M3 `6615c2d` erfolgreich gepusht.

## M5 – Review, Upgrade, Leistung und Übergabe

- Vollständiger isolierter Install-/Upgrade-Testtreiber mit gepinnten Images, internem Netzwerk ohne ausgehenden Netzpfad, eigenem Testfilestore und automatischem Cleanup. Keine echten Kundendaten oder SMTP-Konfiguration.
- Der Testvertrag erhält sein erkennbares Odoo-Manifest ausschließlich in einer ignorierten Laufzeitkopie. Die versionierte Vorlage kann bei Addonsuche kein echtes Helpdesk-Modul überschatten; statisch geprüft. Der Leistungstest verwendet 2.000 unterschiedliche Tickets, um N+1-Abfragen nicht durch wiederholte Ticket-IDs zu verdecken.
- Zusätzliche Prüfungen: direkter Quell-CRUD verweigert, irrtümlich zugeteilter Portal-App-Zugriff verweigert, externe Aktivitätsassignees verweigert, native Formularerstellung/Wizarddefaults, Wizard-Viewvalidierung und Gruppierung/Nummernsuche. Ticketzählercache und Herkunftsreferenzen berücksichtigen aktuelle Rechte.
- Rekursive Selektierbarkeit verhindert die Auswahl unter archivierten Vorfahren; unveränderte Altzuordnungen bleiben editierbar. Batch-Follower verhindern unnötige Einzelabfragen beim Mehrfachanlegen.
- Erste M5-Erweiterung fand eine ungültige False-Domain im Portal-Negativpfad; korrigiert. Native Formularprüfung fand fehlende Initialwerte der readonly Pflichtfelder Nummer/Ersteller; korrigiert, finale Erzeugung bleibt unveränderlich serverseitig. Danach vollständige Suite fehlerfrei bei Installation und Upgrade.
- Ruff-Konfiguration auf Odoo-Konventionen begrenzt; zwei ungenutzte Importe entfernt und Python einheitlich formatiert. Keine zusätzlichen Laufzeitbibliotheken, kein JavaScript.
- Bekannte Image-Diagnostik: Standard-`mail` meldet RST/Docutils-Probleme beim Install; privates Quellenmodell absichtlich ohne ACL mit entsprechender Odoo-Warnung. Kein eigener Testfehler offen.
- Browserwerkzeug konnte wegen `node:process`-Importverweigerung nicht starten. **Keine visuelle Browserabnahme**; native `Form`-/View-Prüfungen sind kein Ersatz.

## Versionierung und nächste Schritte

| Abschnitt | Commit | Push |
|---|---|---|
| M1/Wissensbasis | `45909f4` | erfolgreich |
| M2/Workflow | `25659e7` | erfolgreich |
| M3/Helpdesk-Sicherheit | `6615c2d` | erfolgreich |
| M4/Erhaltender Merge | `27fa520` | erfolgreich |
| M5/Abnahmevorbereitung | `9ef47ad` | erfolgreich |
| CI-Versionen/Nachweise | `e300220` | erfolgreich |

GitHub-Vertragsworkflow aktiv; [Lauf 39678680433](https://github.com/ChrHermes/odoo-anforderungsmanagement/actions/runs/39678680433) für `9ef47ad` **erfolgreich abgeschlossen**, Jobdauer 1m22s. Seine Logs bestätigen 26 Tests nach Install und 26 nach Upgrade sowie 13 SQL-Abfragen im Benchmark. Zwei Wartungshinweise (altes Checkout-Node und wechselndes `ubuntu-latest`) wurden ausschließlich im Workflow behoben: Ubuntu 24.04 und offizieller Checkout-v7.0.1-Commit mit Node 24. [Folgelauf 39679093289](https://github.com/ChrHermes/odoo-anforderungsmanagement/actions/runs/39679093289) für `e300220` **ebenfalls erfolgreich**, Jobdauer 1m38s, keine entsprechenden Runner-/Checkout-Warnungen. App-Code seit `9ef47ad` unverändert; nachfolgende reine Nachweisdokumentation löst gemäß Pfadfilter keinen unnötigen neuen Vertragslauf aus.

**Odoo.sh-Build nicht beobachtet.** Keine direkte Odoo.sh-Konfiguration/Promotion ausgeführt. Development-Pushes können nur nach tatsächlicher Projektzuordnung einem dortigen Build zugeordnet werden. Der Kandidat erfüllt die verfügbaren Offline-Prüfungen, aber noch nicht die verbindliche Enterprise-/Staging-Definition von „fertig“.

Erforderlich: freigegebenen Odoo.sh-Development-Zugang/Projekt identifizieren, Branch-Zuordnung und Schutzregeln bestätigen, Enterprise-Helpdesk inklusive Custom-Views/-Rules bereitstellen, Installation/Upgrade/Browserprüfung und echte Vertraulichkeits-/Mail-Automationsprüfungen ausführen. Erst danach kann ein konkreter Kandidat zur menschlichen Staging-Freigabe vorgelegt werden. Production braucht weiterhin eine separate Freigabe. Anleitung: `README.md`, detaillierte Schritte: `docs/RUNBOOK.md`.
