# Entwicklungsstand

## Naming-/Versionsauftrag – 22.10.2026

N1: Oberfläche auf **Anforderungen**, technische IDs unverändert, Version `18.0.1.1.0`. Deutscher Katalog und Locale-Test ergänzen die bisherige Suite. Finale Install-/Upgradeprüfung einschließlich Katalog vom alten Kandidaten `36085f5` besteht mit 27/26/27 Tests. Statische Prüfung, Ruff und Formatprüfung bestanden. Erweiterte Vorher-/Nachher-Inventur prüft Daten, Archivoriginale, Provenienz, Historie, Aktivitäten, Filestore und Rechte; negative Korruptionsproben greifen.

N1-Commit: `287f078`. N2: separater nativer Port `codex/20.0-port`, Odoo 20.0-20261015/PostgreSQL 17, frischer Vertrag 27 App-Tests + 2 Webtests, Upgrade 27 App-Tests, Inventur inklusive strukturiertem Chatter und negativen Proben bestanden. N3: tatsächlicher Major-Upgrade mangels Enterprise-/Upgradezugang offen; Zugang asynchron angefragt. Keine vollständige Enterprise-Kompatibilität behaupten. [Details, Branchstrategie und Migrationsgates](COMPATIBILITY.md).

Checkout zu Beginn: Nutzeränderungen an `.gitattributes`, Vertragsworkflow, SVG-Icon, Compose, Ruff und Vertragsmanifest (nur CRLF) sowie gelöschte `codex-task.md` und neue `tasks/`. Diese bleiben erhalten und werden nicht in unsere Commits aufgenommen. Remote ist aktuell HTTPS; ausschließlich Development-Pushes.

## Vorheriger Stand – 21.10.2026

**M1–M5 im verfügbaren Offline-Umfang implementiert und lokal geprüft. Enterprise-/Odoo.sh-/Staging-Abnahme weiterhin offen; keine Produktionsfreigabe.**

- `python3 scripts/test_contract.py`: frische Installation **26/26**, tatsächliches Upgrade **26/26**, jeweils 0 Fehler; Upgrade erhält geänderte Seeds, Referenz, Snapshot und physischen Anhang.
- Aggregatlesen: 1.000 Anforderungen / 2.000 unterschiedlichen Tickets und Quellen, kalter Cache, 13 SQL-Abfragen. Native `Form`-Erfassung und Wizard-Defaults geprüft, keine visuelle Browserabnahme.
- Statische Paket-/Python-/XML-Prüfung, Ruff und Formatprüfung bestanden. Reproduzierbare Images und GitHub-Vertragsworkflow vorhanden.
- `README.md`, `DEVELOPMENT_REPORT.md`, `docs/ACCEPTANCE.md`, Wissensbasis und Runbook dienen der Fortsetzung ohne Chatverlauf.
- M1–M5-Commits erfolgreich gepusht; App-Codekandidat `9ef47ad`, anschließend ausschließlich CI-/Nachweisänderungen. GitHub-Vertragsläufe 39678680433 und 39679093289 erfolgreich abgeschlossen; letzterer prüft `e300220` mit fixiertem Ubuntu-24.04-/Checkout-Node-24-Workflow. Git-Log ist die maßgebliche vollständige Commitliste.
- Beide ausschließlich hier erzeugten synthetischen Docker-Teststacks wurden nach den Prüfungen entfernt. Images bleiben als Testcache; lokale ignorierte Testlogs unter `.local/test-results/`.

## Konkrete nächste Schritte / Blocker

1. Freigegebenes Odoo.sh-Projekt, Zuordnung von `codex/initial-mvp` zu Development und technische Staging-/Production-Schutzregeln bestätigen.
2. Lizenziertes Odoo-18-Enterprise-Helpdesk und Custom-Addon-/View-/Rule-Inventar bereitstellen; Addonpfad `addons` überprüfen.
3. Enterprise-Installation und Upgrade mit `--test-tags /gc_requirements` ausführen. Vorhandene Team-/Company-/Feld-/Read-Regeln ergänzend prüfen.
4. UI-Abnahme mit tatsächlichem Browser einschließlich Kanban, Form, Actions, Wizard, Favoriten und archivierten Originalen nachholen. Browserwerkzeug konnte hier nicht starten.
5. M3-Vertraulichkeits- und Mail-/Automationsgate im echten neutralisierten System bestehen; erst danach frische menschliche Kandidatenfreigabe für Staging einholen. Production separat.

Vorhandene Nutzeränderung an `codex-task.md` ist unverändert und wird nicht commit­tet. Keine fremden Branches, Zugangsdaten oder produktiven Daten geändert.

## Auftrag und Plan

Autonome Erstimplementierung M1–M5 auf `codex/initial-mvp`; keine Staging-/Production-Aktionen. Der aktuelle Auftrag erlaubt bei fehlender Enterprise-Laufzeit statische und isolierte Prüfungen und verlangt die Kennzeichnung ungeprüfter Integrationstests. Sicherheitsgates bleiben Freigabeblocker; implementierter Code allein schließt keinen Meilenstein ab.

1. **Vorbereitung:** Spezifikationen lesen, Wissen initialisieren, Git/Dependencies/Testmöglichkeiten prüfen.
2. **M1:** Modelle, Stammdaten, Referenz, Gruppen, native Grundansichten; Modell-/XML-/ACL-Prüfungen.
3. **M2:** Workflow/Wizards, interne Zusammenarbeit, Suche und vollständige Oberfläche; negative ORM-Prüfungen.
4. **M3:** private Quellen, aktuelle Ticketrechte, Ticketaktionen, Kundenaggregation, interne Notizen; ausführliche Sicherheitsprüfungen.
5. **M4:** deterministische Duplikatvorschläge, bestätigte verlustfreie Zusammenführung, Archivierung; Historienprüfungen.
6. **M5:** kritischer Review, Installations-/Upgrade-/Leistungsprüfungen soweit verfügbar, Betriebs- und Fortsetzungsanleitung.

## Nachweise

- Alle vier verbindlichen Spezifikationsdateien vollständig gelesen.
- Branch und Remote geprüft; nicht-interaktives `git ls-remote` erfolgreich. Remote-Branch ungeschützt; tatsächliche Odoo.sh-Zuordnung und Schutz vor Staging/Production nicht bestätigt. Deployment bleibt gesperrt.
- Keine lokale Odoo-/Enterprise-Installation; Docker verfügbar. Enterprise-Quellcodezugriff nicht vorhanden (GitHub 404).
- Dokumentationsbasis vor Implementierungsbeginn gefüllt.

## Verlauf M1/M2

M1 und M2 implementiert; zunächst 7 Odoo-18-TransactionCase-Tests im synthetischen Vertrag bestanden. M2 umfasst flexible Übergänge, neue Pflichtbegründung je Übergang, Veröffentlichungsdatum, interne Follower mit direktem ORM-Schutz, Notizen/Aktivitäten, Statuswizard und Suchfilter. Erster M1-Lauf: 2 Testfehler (Exception-Erwartungen), korrigiert; Wiederholung: 0 Fehler. Installation/XML erfolgreich im isolierten Community-Vertrag. Enterprise-Nachweise bleiben offen.

Enterprise-Installation, bestehende Helpdesk-Customizations, echte Record Rules und Odoo.sh-Build bleiben nachzuweisen. Nutzeränderung `codex-task.md` nicht committen.

### M3, implementiert / Enterprise-Gate offen

17 Tests im Community-Vertrag erfolgreich, 0 Fehler. Enthalten: n:m-Capture, unveränderlicher Snapshot, getrennte Redaktion, Kundendeduplizierung/-änderung, Ticketwizard, native Actions, genaue eigene Ticketregel, ACL-Verweigerung, alternative Schnittstellen, Rechteentzug, interne Notizen ohne Notification-Pipeline. Erster M3-Lauf: 8 Fehler (fehlende frühe Pflichtfeldvalidierung und Test-Exportberechtigung); behoben und wiederholt. M4 wird gemäß aktuellem Offline-Auftrag implementiert, ohne das M3-Enterprise-Gate als bestanden auszuweisen.

### M4, implementiert / Enterprise-Gate offen

21 Tests im Community-Vertrag erfolgreich. Bestätigter Merge, Zeilensperren, Quellenkopien mit Provenienz, unveränderte überlappende Snapshots, manuelle Kundenzuordnung, Historie/Anhänge/Aktivitäten, dauerhafte Redirects/Ketten, Wiederherstellung und bounded Duplikatvorschläge. Erster Lauf: zwei Fehler; Odoo-Standardlöschung von Aktivitäten korrigiert, NewId-Erwartung im Vorschlagstest an tatsächliche ORM-Semantik angepasst. M5 ergänzt anschließend die oben dokumentierten Installations-/Upgrade-/Leistungsnachweise.

Push am 22.10.2026 versucht, nicht möglich: HTTPS-Anmeldung fehlt (`could not read Username`); lesender SSH-Fallback scheitert an fehlendem bestätigtem GitHub-Hostschlüssel. Keine Zugangsdaten-/Remote-/SSH-Konfiguration geändert. Commits bleiben lokal; kein aktueller GitHub-/Odoo.sh-Build beobachtet.

Finale Wiederholung nach verstärkter Historien-Fixture: 18 27/26/27 Tests, 20 29/27 Tests, beide Inventuren und negativen Proben bestanden. Zwei tatsächlich vorhandene Trackingzeilen und ursprüngliche Eindeutigkeitsnamen auf 20 bestätigt. Beide Teststacks entfernt; statische Prüfung, Ruff und Formatprüfung je Versionslinie erfolgreich. Enterprise-/Migrationsgate bleibt offen.
