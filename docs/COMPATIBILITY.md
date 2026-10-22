# Versionen, Wartung und Migration

Stand: 22.10.2026. Sichtbarer Name **Anforderungen**, technischer Modulname `gc_requirements`. Odoo 18 bleibt Entwicklungs- und Abnahmebasis. Ziel ist vollständige Unterstützung von 18 und 20 Enterprise; **keine der beiden Enterprise-Versionen ist bisher abgenommen**.

## Nachweismatrix

| Prüfung | Odoo 18 | Odoo 20 |
|---|---|---|
| Offizielle Community-Laufzeit | `18.0-20261015`, per Digest fixiert | `20.0-20261015`, Odoo-Digest `61e3c71b…`, PostgreSQL 17 (Digest fixiert) |
| Frische Vertragsinstallation | 27 Tests bestanden | 27 App-Tests plus 2 zusätzliche Webtests bestanden |
| Modulupgrade im Vertrag | 27 Tests bestanden; bisheriger Kandidat `36085f5` vorher mit 26 Tests installiert | 27 App-Tests bestanden |
| Daten-/Filestore-Erhalt im Vertrag | Erweiterte Inventur und negative Korruptionsproben bestanden | Dieselben Prüfungen einschließlich strukturierter Historie bestanden |
| Enterprise-Helpdesk: Install/Upgrade | Nicht ausgeführt | Nicht ausgeführt |
| Enterprise-/Custom-Regeln und Mailautomationen | Nicht ausgeführt | Nicht ausgeführt |
| Browser-/Launcher-/Widget-Abnahme | Nicht ausgeführt | Nicht ausgeführt |
| Tatsächliche Datenbankmigration 18 -> 20 | **Nicht ausgeführt; blockiert durch fehlenden lizenzierten Zielzugang und freigegebenen Upgradeweg** | Kein Ersatz durch Neuinstallation/Import oder `-u` |

Ein Vertragslauf nutzt echte Odoo-ORM-, Mail- und XML-Laufzeit, aber ein ausdrücklich synthetisches Helpdesk-Modell. Das belegt die geprüften App-Pfade, niemals vollständige Enterprise-Kompatibilität. Alte Prüfungen bleiben erhalten; neue Sprach-/Erhaltungsprüfungen ergänzen sie. Ergebnisse gelten nur für den jeweiligen Git-Kandidaten und Image-Digest.

## Branch- und Wartungsstrategie

- `codex/initial-mvp`: bestehender autorisierter Development-Branch für 18, Manifest `18.0.1.1.0`.
- `codex/20.0-port`: separate Development-Portierung vom gemeinsamen Naming-/Teststand, Manifest `20.0.1.1.0`. Kein Merge des 20er Sicherheits-/API-Codes in 18.
- Gemeinsame Fehlerkorrekturen zuerst auf der primären 18er Linie, danach gezielt nach 20 übernehmen und dort vollständig testen. Versionsbedingte Korrekturen nur in ihrer Linie. Gleiche Modelle/XML-IDs und gleichwertige Testassertionen behalten; keine doppelte App und keine parallele Datenhaltung.
- Nach Abnahme können menschlich eingerichtete Wartungsbranches `18.0` und `20.0` sinnvoll sein. Dies ist ein Vorschlag, keine Anlage/Promotion von Odoo.sh-Branches. Git-Push allein belegt weder Odoo.sh-Zuordnung noch sichere Deploymentrechte.
- Jeder Branch prüft sein natives Manifest und seine fixierte Laufzeit. Ein künstliches Manifest-Umschreiben innerhalb einer Testmatrix würde Versionsunterschiede verdecken.

## Befund aus offiziellen 20er Quellen und Image

Odoo 20 ist verfügbar; keine Anpassung auf Basis einer vermuteten zukünftigen API. 18 nutzt `base`, `mail`, `helpdesk`; 20 ergänzt das offizielle `mail_tracking`, da strukturierte Änderungswerte aus `mail` ausgelagert wurden. Das Image enthält kein Enterprise-Helpdesk.

| Bereich | Prüfpunkt für den separaten Port |
|---|---|
| ORM | `models.Constraint`, `Domain.AND/OR` und natives `read_group(groupby=..., aggregates=...)`; Eindeutigkeit und Such-/Exportabwehr bleiben erhalten |
| Benutzer/Gruppen | `res.users.group_ids` für direkte, `all_group_ids` für effektive Mitgliedschaften; `res.groups.privilege_id` statt direkter Kategorie; implizite Config-Mitgliedschaft weiterhin berücksichtigen |
| ACLs/Rules | `ir.access` ersetzt `ir.model.access`/`ir.rule`; gruppengebundene Berechtigungen und globale Einschränkungen mit `operation`/`domain`. Vorhandene XML-IDs behalten, private Quellen weiterhin ohne allgemeine Berechtigung. Native Ticket-Bindings mit `group_ids`, keine erfundenen Helpdesk-XPaths |
| Chatter/Mail | `_notify_get_recipients` hat in 20 keine separate `msg_vals`-Position. `mail_tracking` ist zusätzlich erforderlich, um strukturierte `tracking_value_ids` zu erhalten; keine Historie aus der Erhaltungsprüfung streichen. Interne Empfängerfilter und Note-Service bleiben abgesichert |
| Aktivitäten/Archivierung | Originalaktivität beim Merge/Archivieren und reguläres Erledigen erneut prüfen |
| XML/Widgets | `<list>`, Kanban-`card`, Such-/Wizard-/Formarchitektur laden. Suchgruppen ohne die alten `expand`-/`string`-Attribute. Visuelles Verhalten separat abnehmen |
| Anhänge/Testparameter | Physischer Inhalt über `ir.attachment.raw.content` (lazy BinaryValue) statt entfallenem `datas`; Testfixture nutzt typisierte `set_str`/`get_str`-Parameter |
| Infrastruktur | Offizielle 20er `release.py` verlangt PostgreSQL mindestens 16; nicht den 18er PostgreSQL-15-Stack unverändert übernehmen |

Primärquellen, am 22.10.2026 gelesen: [Release/Anforderungen](https://github.com/odoo/odoo/blob/20.0/odoo/release.py), [Benutzer](https://github.com/odoo/odoo/blob/20.0/odoo/addons/base/models/res_users.py), [Gruppen](https://github.com/odoo/odoo/blob/20.0/odoo/addons/base/models/res_groups.py), [Actions](https://github.com/odoo/odoo/blob/20.0/odoo/addons/base/models/ir_actions.py), [Zugriffsmodell](https://github.com/odoo/odoo/blob/20.0/odoo/addons/base/models/ir_access.py), [Anhänge](https://github.com/odoo/odoo/blob/20.0/odoo/addons/base/models/ir_attachment.py), [Mail](https://github.com/odoo/odoo/blob/20.0/addons/mail/models/mail_thread.py), [offizielle Images](https://hub.docker.com/_/odoo). Runtimeprüfung geht einer Kompatibilitätsaussage vor.

## Notwendiger Migrationsablauf

1. Freigegebene isolierte Enterprise-Development-Kopie von Datenbank **und Filestore**, Versions-/Addon-/Custom-/Rule-Inventar und benannte Testidentitäten bereitstellen. Vor Datenoperationen Mail und externe Integrationen isolieren. Staging separat genehmigen lassen.
2. Den 18er Kandidaten mit allen bisherigen Tests und ergänzenden Erhaltungsprüfungen testen. Schreibzugriffe während der Inventur sperren, damit Vorher/Nachher vergleichbar sind. Backup und getesteten Wiederherstellungsweg sichern.
3. `scripts/migration_audit.py` in einer administrativen Odoo-Shell laden und `capture(env, [<berechtigter-testbenutzer>, <eingeschränkter-testbenutzer>, <portal-testbenutzer>])` erfassen. Inventur außerhalb Git geschützt speichern. Sie enthält IDs/Hashes, keine Klartexte, ist aber dennoch vertraulich. Keine echten Daten an nicht genehmigte Dienste senden.
4. Die vollständige Kopie über den genehmigten offiziellen Odoo-Upgradeweg auf 20 heben. Den 20er Addonbranch bereitstellen und `gc_requirements` aktualisieren. **Kein Odoo 20 direkt auf einem 18er Schema starten.** Ein eigenes SQL-Skript für Odoo-Core wird hier nicht erfunden.
5. Auf dem migrierten Bestand `verify(env, baseline)` ausführen. Erfasst werden Nummern/Sequenz, Redaktion/Workflow, komplette Klassifikation, Ticketverknüpfungen und private Snapshots samt Capture-/Mergeprovenienz, manuelle Kunden, physische Anhänge, Nachrichten/Tracking, Follower/Aktivitäten, archivierte Originale/Redirects, XML-IDs, ACLs/Rules, effektive Gruppenmitgliedschaft und aktuelle Sichtbarkeit je Testbenutzer. Abweichungen stoppen die Abnahme; das Tool repariert oder lockert keine Daten/Rechte. Legitimer upstreambedingter ACL-/Historienwandel benötigt dokumentierten Review und zusätzliche Rechteprüfungen.
6. Gesamte Odoo-Tests unter 20, Formular-/Wizard-/Launcherprüfung sowie echte Ticketrechte inklusive Rechteentzug/Portal/RPC/Export und Mail-/Automationsnebenwirkungen nachprüfen. Ein Quellenhash allein beweist keine Vertraulichkeit. Neue REQ-Nummer prüfen, ohne den alten Zähler zurückzusetzen.
7. Kandidaten- und Laufzeit-SHAs, Upgradebericht, Inventurdifferenzen und Testergebnisse dokumentieren. Erst mit diesen Nachweisen von erfolgreicher Migration sprechen. Frische Businessfreigabe für Staging, danach separate Production-Freigabe und eingeschränkter benannter Pilot.

Die fachlichen Addonmodelle/Tabellen/Felder/XML-IDs bleiben identisch; die Sicherheitsdatensätze wechseln in 20 auf das neue Coremodell `ir.access` und erhalten zusätzlich einen nativen Gruppenscope. Die offizielle Migration muss bestehende Sicherheitsmetadaten und XML-ID-Ziele korrekt übertragen. Der Inventurprüfer normalisiert die Coremodell-/Gruppenfeldnamen und vergleicht Policydefinitionen sowie tatsächliche Lesepfade; zusätzliche XML-IDs sind erlaubt, bestehende fachliche Ziele müssen erhalten bleiben. Änderungen der effektiven Rechte oder Definitionen bleiben ein Reviewblocker. Deshalb deshalb keine vorsorgliche Datenumschreibung oder Snapshot-Neuerfassung. Ein erforderliches gezieltes Addon-Migrationsskript wird erst anhand eines beobachteten echten Upgradebefunds entwickelt. Grundlage: [offizieller Ablauf für eigene Module](https://www.odoo.com/documentation/20.0/developer/howtos/upgrade_custom_db.html).

## Noch offene Risiken

Lizenzierter Enterprise-Zugriff fehlt; `git ls-remote` kann das private Repository ohne Zugang nicht lesen. Odoo.sh-Projekt, Development-Zuordnung und technische Deploymentgrenzen sind nicht bestätigt. Reale Helpdesk-Feld-/Team-/Company-Regeln, Automationen, Mailnebenwirkungen, visuelle UI und echter Major-Upgrade sind weiterhin Freigabeblocker. Keine Staging-/Production-Aktion wurde hieraus abgeleitet.

## Laufnachweise, 22.10.2026

- 18: `python3 scripts/test_contract.py --baseline-ref 36085f50b66102a85515fd004abae59120848af1`, finaler Lauf mit 27/26/27 Tests und Inventur erfolgreich. Zählerlesen: frisch 12, nach Upgrade 13 SQL-Abfragen für 1.000 REQs/2.000 Tickets. Cleanup erfolgreich. Naming-Codecommit `287f078`; gemeinsamer Inventur-/Treiberabschluss im aktuellen Git-Log.
- 20: Code-/Dokumentationskandidat `30735e8` auf `codex/20.0-port` `python3 scripts/test_contract.py --keep`, frischer Install 29 Tests (27 App + 2 Web), Upgrade 27, jeweils null Fehler; Vorher-/Nachher-Inventur und negative Proben erfolgreich. Zählerlesen jeweils 5 SQL-Abfragen bei identischer Fixture. Kein Last-/Parallelbenutzerbenchmark. Logs im jeweiligen ignorierten `.local/test-results/`.
- Fehlgeschlagene 20er Vorläufe wurden korrigiert: entfallene ACL-/Rule-Modelle, alte Suchgruppenattribute, Anhangs-`datas` bzw. lazy BinaryValue, typisierte Systemparameter und ausgelagertes strukturiertes Tracking. Kein Test entfernt oder umgangen.
- Statische Paket-/Python-/XML-/ACL-Prüfung, Ruff und Formatprüfung werden pro Versionslinie ausgeführt. Ablehnung einer anderen Majorversion als Vertragsbaseline explizit geprüft.
- Odoo.sh-/Enterprise-/Major-Migrations- und visuelle Nachweise bleiben offen. Ein lokaler Vertragslauf belegt keinen gehosteten Development-Build.

Eine zusätzliche Historienprobe deckte eine leere Trackingfixture im ursprünglichen Erstellungs-Transaktionskontext auf. Die verstärkte Fixture persistiert zuerst die Erstellung, erzeugt danach eine echte getrackte Änderung und verlangt vorhandene strukturierte Trackingzeilen vor dem Vorher-/Nachhervergleich. Damit kann ein leerer Historiensatz nicht als Erhaltungsnachweis genügen.

Development-Push ist auf diesem Rechner mangels HTTPS-Anmeldung bzw. bestätigtem SSH-Zugang nicht möglich; keine neuen Remote-/CI-/Odoo.sh-Ergebnisse behaupten. Änderungen werden lokal auf den beiden Development-Branches committed.

Die abschließende 20er Detailprobe bestätigt zwei erhaltene strukturierte Trackingzeilen sowie die ursprünglichen SQL-Constraintnamen `gc_requirement_reference_unique` und `gc_requirement_ticket_source_requirement_ticket_unique`. Beide synthetischen Teststacks wurden anschließend entfernt. Statische Prüfung, Ruff und Formatprüfung sind auf beiden Linien bestanden.
