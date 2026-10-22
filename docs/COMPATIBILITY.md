# Versionen, Wartung und Migration

Stand: 22.10.2026. Sichtbarer Name **Anforderungen**, technischer Modulname `gc_requirements`. Odoo 18 bleibt Entwicklungs- und Abnahmebasis. Ziel ist vollständige Unterstützung von 18 und 20 Enterprise; **keine der beiden Enterprise-Versionen ist bisher abgenommen**.

## Nachweismatrix

| Prüfung | Odoo 18 | Odoo 20 |
|---|---|---|
| Offizielle Community-Laufzeit | `18.0-20261015`, per Digest fixiert | `20.0-20261015`, Image und Upstream geprüft |
| Frische Vertragsinstallation | 27 Tests bestanden | Portierung ausstehend |
| Modulupgrade im Vertrag | 27 Tests bestanden; bisheriger Kandidat `36085f5` vorher mit 26 Tests installiert | Portierung ausstehend |
| Daten-/Filestore-Erhalt im Vertrag | Erweiterte Inventur und negative Korruptionsproben bestanden | Ausstehend |
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

Odoo 20 ist verfügbar; keine Anpassung auf Basis einer vermuteten zukünftigen API. Abhängigkeiten bleiben `base`, `mail`, `helpdesk`. Das Image enthält kein Enterprise-Helpdesk.

| Bereich | Prüfpunkt für den separaten Port |
|---|---|
| ORM | Neue native Constraint-/Domain-/Gruppierungs-APIs prüfen; Eindeutigkeit und Such-/Exportabwehr erhalten |
| Benutzer/Gruppen | `res.users.group_ids` für direkte, `all_group_ids` für effektive Mitgliedschaften; `res.groups.privilege_id` statt direkter Kategorie; implizite Config-Mitgliedschaft weiterhin berücksichtigen |
| Actions/Rules | Gruppenfelder gegen die installierte 20er Laufzeit prüfen; Bindings bleiben native Ticketaktionen ohne erfundene Helpdesk-XPaths |
| Chatter/Mail | `_notify_get_recipients` hat in 20 keine separate `msg_vals`-Position; interne Empfängerfilter und Note-Service unverändert absichern |
| Aktivitäten/Archivierung | Originalaktivität beim Merge/Archivieren und reguläres Erledigen erneut prüfen |
| XML/Widgets | `<list>`, Kanban-`card`, Such-/Wizard-/Formarchitektur laden; visuelles Verhalten separat abnehmen |
| Infrastruktur | Offizielle 20er `release.py` verlangt PostgreSQL mindestens 16; nicht den 18er PostgreSQL-15-Stack unverändert übernehmen |

Primärquellen, am 22.10.2026 gelesen: [Release/Anforderungen](https://github.com/odoo/odoo/blob/20.0/odoo/release.py), [Benutzer](https://github.com/odoo/odoo/blob/20.0/odoo/addons/base/models/res_users.py), [Gruppen](https://github.com/odoo/odoo/blob/20.0/odoo/addons/base/models/res_groups.py), [Actions](https://github.com/odoo/odoo/blob/20.0/odoo/addons/base/models/ir_actions.py), [Mail](https://github.com/odoo/odoo/blob/20.0/addons/mail/models/mail_thread.py), [offizielle Images](https://hub.docker.com/_/odoo). Runtimeprüfung geht einer Kompatibilitätsaussage vor.

## Notwendiger Migrationsablauf

1. Freigegebene isolierte Enterprise-Development-Kopie von Datenbank **und Filestore**, Versions-/Addon-/Custom-/Rule-Inventar und benannte Testidentitäten bereitstellen. Vor Datenoperationen Mail und externe Integrationen isolieren. Staging separat genehmigen lassen.
2. Den 18er Kandidaten mit allen bisherigen Tests und ergänzenden Erhaltungsprüfungen testen. Schreibzugriffe während der Inventur sperren, damit Vorher/Nachher vergleichbar sind. Backup und getesteten Wiederherstellungsweg sichern.
3. `scripts/migration_audit.py` in einer administrativen Odoo-Shell laden und `capture(env, [<berechtigter-testbenutzer>, <eingeschränkter-testbenutzer>, <portal-testbenutzer>])` erfassen. Inventur außerhalb Git geschützt speichern. Sie enthält IDs/Hashes, keine Klartexte, ist aber dennoch vertraulich. Keine echten Daten an nicht genehmigte Dienste senden.
4. Die vollständige Kopie über den genehmigten offiziellen Odoo-Upgradeweg auf 20 heben. Den 20er Addonbranch bereitstellen und `gc_requirements` aktualisieren. **Kein Odoo 20 direkt auf einem 18er Schema starten.** Ein eigenes SQL-Skript für Odoo-Core wird hier nicht erfunden.
5. Auf dem migrierten Bestand `verify(env, baseline)` ausführen. Erfasst werden Nummern/Sequenz, Redaktion/Workflow, komplette Klassifikation, Ticketverknüpfungen und private Snapshots samt Capture-/Mergeprovenienz, manuelle Kunden, physische Anhänge, Nachrichten/Tracking, Follower/Aktivitäten, archivierte Originale/Redirects, XML-IDs, ACLs/Rules, effektive Gruppenmitgliedschaft und aktuelle Sichtbarkeit je Testbenutzer. Abweichungen stoppen die Abnahme; das Tool repariert oder lockert keine Daten/Rechte. Legitimer upstreambedingter ACL-/Historienwandel benötigt dokumentierten Review und zusätzliche Rechteprüfungen.
6. Gesamte Odoo-Tests unter 20, Formular-/Wizard-/Launcherprüfung sowie echte Ticketrechte inklusive Rechteentzug/Portal/RPC/Export und Mail-/Automationsnebenwirkungen nachprüfen. Ein Quellenhash allein beweist keine Vertraulichkeit. Neue REQ-Nummer prüfen, ohne den alten Zähler zurückzusetzen.
7. Kandidaten- und Laufzeit-SHAs, Upgradebericht, Inventurdifferenzen und Testergebnisse dokumentieren. Erst mit diesen Nachweisen von erfolgreicher Migration sprechen. Frische Businessfreigabe für Staging, danach separate Production-Freigabe und eingeschränkter benannter Pilot.

Die Addonmodelle/Tabellen/Felder/XML-IDs bleiben derzeit identisch; deshalb keine vorsorgliche Datenumschreibung oder Snapshot-Neuerfassung. Ein erforderliches gezieltes Addon-Migrationsskript wird erst anhand eines beobachteten echten Upgradebefunds entwickelt. Grundlage: [offizieller Ablauf für eigene Module](https://www.odoo.com/documentation/20.0/developer/howtos/upgrade_custom_db.html).

## Noch offene Risiken

Lizenzierter Enterprise-Zugriff fehlt; `git ls-remote` kann das private Repository ohne Zugang nicht lesen. Odoo.sh-Projekt, Development-Zuordnung und technische Deploymentgrenzen sind nicht bestätigt. Reale Helpdesk-Feld-/Team-/Company-Regeln, Automationen, Mailnebenwirkungen, visuelle UI und echter Major-Upgrade sind weiterhin Freigabeblocker. Keine Staging-/Production-Aktion wurde hieraus abgeleitet.
