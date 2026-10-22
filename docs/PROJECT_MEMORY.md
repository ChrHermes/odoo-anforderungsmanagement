# Projektwissen

## Manuelle Release-/Meilensteinstatus, 22.10.2026

Versionen 18.0.1.3.1 / 20.0.1.3.1, Auftrag release-refining, SPEC §14.1 / D020. `state` war bereits gespeicherte manuelle Selection. Bestehender `gc.requirement.milestone.complete` plus XML-ID/ACL wiederverwendet: allgemeines `action_change_state`, freie Auswahl, Abschlusskurzbefehle default done. Kein neues Statusmodell/keine Migration. Abschlussdatum serverseitig nur bei tatsächlichem Übergang nach done; Wiederöffnung und wiederholtes/mischendes Batch-write erhalten früheres Datum. Datierte Abschlussnotiz plus natives Tracking behalten Historie.

Neue nichtgespeicherte `implementation_summary` und `not_implemented_count` nutzen denselben normalen Benutzeraggregatpfad. Zusammenfassung/Prozent behalten alten Nenner aktive ohne Abgelehnte; Abschlusswarnung zählt präziser alle lesbaren nicht umgesetzten Zuordnungen inklusive Archiv/Abgelehnt. Status/Pub-Daten der Requirements bleiben unabhängig. Native Kanban-Prozentanzeige ohne zusätzliches `title` (langer Titel verdrängte/wickelte 100 %); daneben explizite Zusammenfassung mit Tooltip. Checkbox mit explizitem vollbreitem Label statt schmaler Standard-Gruppenlabelspalte.

Tests: 18 Altupgrade 49/42/49, befüllt 49/49; 20 51/44/49 und 51/49; Inventuren erhalten wieder geöffnetes Release und abgeschlossenen Meilenstein mit historischen Daten. Native Chatter-Metadaten nur als administrativer Testbeobachter lesen; eigentliche Aktionen bleiben mit Pilotbenutzer. Im Test zuerst `_track_finalize()` auf frischem Plan, damit native Erstellungsunterdrückung endet. Keine App-Sudo-Erweiterung.

Browserdaten können vom Nutzer bearbeitet/archiviert sein: Planungssmoke setzt keinen bestimmten Seedtitel mehr voraus und erstellt eigene Prüfdatensätze. Erwartete Server-Validation öffnet zusätzlichen Fehlerdialog; gezielt dessen Footer-Schließen bedienen, nicht früher aufgelösten Hintergrund-Schließenbutton. Vorhandene Demo niemals zurücksetzen. Lokale Browsernachweise nur für 18/synthetisch; Enterprise/20-Browser/Major-Migration bleiben offen.


Abschluss UX, 22.10.2026: Kandidaten 18 `bc2cc78`, 20 `c15a70e`. Finale normale Verträge erneut 32/32 (18) beziehungsweise 34/32 (20) einschließlich Farberhalt/Inventur bestanden, beide 18er Browserchecks inklusive Tooltips und negativem Config-/Snapshotzugriff erfolgreich. Beide Branch-Pushes tatsächlich versucht und mangels HTTPS-Anmeldung mit Exit 128 gescheitert (`could not read Username`). Kein aktueller Remote-/CI-/Odoo.sh-/Enterprise-Nachweis. Die laufende lokale 18er Demo bleibt davon unabhängig. Dokumentationsabschluss im nachfolgenden Commit.

## UX-Stand 18/20, 22.10.2026

Die interaktive lokale Demo und Browserhilfen liegen ausschließlich im primären 18er Checkout, nicht in diesem 20er Port.


- Addon 18.0.1.2.0 / 20.0.1.2.0; fünf Produkte mit exakten Defaults: Node #0068b1, Operator #40d0d7, Core #4a0a7c, Nexus #c51a82, Allgemeines #fa4d0f. `color_hex` optional/regexvalidiert; `color_text` berechnet sRGB-Kontrast. Native `color`-Char-Widgets sind in beiden tatsächlich geprüften Images vorhanden; keine Palette oder zusätzliches JS nötig.
- `_ensure_default_products` aus `data/product_defaults.xml` läuft bei Install/Upgrade. Bestehende XML-ID gewinnt; andernfalls vorhandenes gleichnamiges Produkt übernehmen, nur fehlendes anlegen. Nur leere Farbe ergänzen. Neue XML-IDs noupdate; alte Seeds unverändert geschützt, keine neuen Kategorien. Individuelle Farbe und vorhandenes manuelles Nexus sind durch echte Upgradefixture geprüft.
- `state.group_expand=True` plus Kanban `default_order="state asc, priority desc, write_date desc"`, Kontext read_group_expand. 18 formatierte read_group, 20 formatted_read_group mit nativem Kontext; leere und gefilterte Gruppen testen. Odoo 20 wertet die Erweiterung ohne diesen Webkontext absichtlich nicht aus. Gruppen-DOM nutzt generische datapoint-IDs, daher schmale XML-Template-Erweiterung für ein ausschließlich model-/stategebundenes Datenattribut; in 20 `this.props`, in 18 `props`. CSS nur `.gc_requirements_kanban`.
- `category_path` relativ, vollständiger category_id-Pfad als Tooltip; Produkt-/Typbadges, drei Sterne und übrige Karteninfos erhalten. Quelle bleibt im privaten Adapter/Transient-Wizard, kein Snapshot-HTML am Requirement. Leerfall mit Ticketcount 0 ausdrücklich beschriftet. Rechte-/Revocation-/Such-/Exporttests unverändert plus zusätzliche UX-Proben.
- UI-Demo ergänzt idempotent zwei lokale Produktbeispiele und `restricted_developer`, interner App-/Export-Benutzer ohne Config/Helpdesk. Getrennte zufällige Zugangsdaten über `credentials --restricted`, nur ignorierte lokale Datei. Synthetischen Modulnamen unbedingt in en_US prüfen: deutsche Coreübersetzung nennt das Ersatzmodul „Kundendienst“ und verdeckt den synthetischen Marker.
- Testtreiber-Befund: bei Baseline-Upgrades auch die Vorher-Fixture mit dem **alten** Addonmount ausführen. Aktuellen Registrycode vor Schemaupgrade zu laden führte zu fehlender color_hex-Spalte. Generic Inventur bleibt strikt; nur der konkrete Vertrag erlaubt enumerierte neue Seed-IDs und prüft bestehende Produkt-/Farbhashes unverändert.
- Vertragsnachweise: 18 Altupgrade 32/27/32 und normal 32/32; 20 Altupgrade 34/29/32 (frisch inkl. 2 Core-Webfällen) und normal 34/32. Erhaltungsinventuren, negative Proben, individueller Farberhalt bestanden. Keine Enterprise- oder echte Major-Migrationsabnahme.
- `scripts/browser_ux.mjs` unter 18 tatsächlich erfolgreich, Artefakte in `.local/dev/browser-ux/`: Kanban, Endspalten, leer/schmal, Produktkonfiguration, erlaubte/gesperrte Quelle und kein Ticket. Rechtefälle mit zwei echten Browserkontexten und generischen RPCs. Standardfarben werden für den Smoke erwartet, individuelle Benutzerfarben nicht ohne Entscheidung zurücksetzen. Quelle-/Konfigurations-/Kanbanbilder visuell geprüft; 20 visuell weiter offen.

Stand: 22.10.2026. Verbindliche Fachentscheidungen stehen in `SPEC.md`, technische Regeln in `TECHNICAL_DESIGN.md`, Prüfgates in `IMPLEMENTATION.md` und Arbeitsregeln in `AGENTS.md`.

- Eigenständiges internes Odoo-18-Enterprise-Addon `addons/gc_requirements`, native Python/XML-Komponenten, deutsche Oberfläche. Abhängigkeiten: `base`, `mail`, `helpdesk`.
- Explizite Pilotgruppe; Konfigurationsgruppe verwaltet ausschließlich Produktstammdaten. Keine pauschale Berechtigung für interne Mitarbeiter.
- Ein Produkt und optional ein beliebig tiefer Funktionsbereich. Seedstruktur aus SPEC §3 als upgradegeschützte Installationsdaten.
- Redaktionelle Beschreibung und unveränderliche Ticketquelle bleiben getrennt. Ticketquellen sind privat; jede Anzeige prüft die aktuellen Leserechte auf das konkrete Helpdesk-Ticket.
- Acht flexible Zustände; neue Begründung bei jeder Zurückstellung/Ablehnung; Umgesetzt bedeutet veröffentlicht. Nur interne Ticketnotizen bei Geplant/Umgesetzt/Abgelehnt.
- Kunden zählen nach `commercial_partner_id`; manuelle Kundenbeziehungen bleiben unabhängig. Keine externen Follower, keine automatischen Aktivitäten.
- Zusammenführen erhält Originale, Quellen, Historie und Anhänge; archivierter Verlierer mit dauerhaftem Verweis. Keine normale Löschung.
- Autorisierter Arbeitsbranch: `codex/initial-mvp`. Bestätigtes Remote: `git@github.com:ChrHermes/odoo-anforderungsmanagement.git`. Kein Force-Push, kein Merge in andere Branches.
- Anfangsbefund: Repository enthält nur Spezifikationen und leere Wissensdateien; lokale Änderung an `codex-task.md` stammt vom Nutzer und bleibt unberührt. Python 3.12 und Docker verfügbar, Odoo/Enterprise lokal nicht installiert. GitHub-Zugriff auf `odoo/enterprise` liefert 404. Kein identifiziertes Odoo.sh-Projekt und keine bestätigten Deployment-Schutzregeln.

Fortsetzung: zuerst `docs/STATUS.md`, `docs/DECISIONS.md`, `docs/RUNBOOK.md` und `DEVELOPMENT_REPORT.md` lesen, dann Git-Status/Log prüfen. Prüfresultate aus isoliertem Ersatzvertrag gelten niemals als Enterprise-Abnahme.

Verifizierte Odoo-18-Details: `<list>` und Kanban-Template `card` werden akzeptiert; `_has_cycle()` ist die aktuelle Hierarchie-API. `check_access()` verbindet ACL und Record Rules. `mail.followers` benötigt zusätzlich einen Constraint, um direkte ORM-/One2many-Einträge externer Partner abzuweisen. `new_test_user` mit `no_reset_password=True` verwenden, um synthetische Signup-Mails zu vermeiden.

Quellenschutz: keine ACL und keine öffentliche Relation zu `gc.requirement.ticket.source`; `get_authorized_sources()` prüft Parent und Ticket ohne sudo, bevor privater Snapshot gelesen wird. Viewer-HTML ist nicht gespeichert und wird bei Read/Search_read/Export neu autorisiert. Kein Snapshot-Text in Chatter. `base.group_allow_export` muss in Export-Sicherheitstests ausdrücklich gesetzt sein, damit die Tests tatsächlich die Modell-ACL prüfen.

## Verifizierter Abschlussstand des Offline-Kandidaten

- Odoo Community **18.0-20261015**, PostgreSQL 15, per Digest fixierte Docker-Images. 26 Tests jeweils bei frischer Installation und bei echtem Upgrade bestanden. `scripts/test_contract.py` ist der portable reproduzierbare Einstieg; entfernt nur seinen synthetischen Stack. Keine Enterprise-Abnahme daraus ableiten.
- Der synthetische Vertrag ist nur eine Vorlage ohne erkennbares Odoo-Manifest. `test_contract.py` erzeugt eine Laufzeitkopie in `.local/contract-addons`; diese niemals deployen. Nur `addons/gc_requirements` enthält ein versioniertes echtes Manifest. Keine Quell-/Config-ACL für Snapshots ergänzen, auch wenn Odoo davor warnt.
- 1.000 Anforderungen mit 2.000 unterschiedlichen Tickets und Quellen: Zählerlesen mit kaltem Cache in 13 SQL-Abfragen. Follower werden beim Batch-Create pro Benutzer gesammelt.
- Odoo-`Form` verlangt bei readonly Pflichtfeldern Initialwerte: Nummer zeigt vor Save „Neu“, Ersteller aktuellen Benutzer. Serverseitig werden beide unveränderlich gesetzt; Clientwerte können sie nicht bestimmen.
- Kanonische falsche Odoo-Domain ist `[(0, '=', 1)]`; der Negativtest mit versehentlich berechtigtem Portalbenutzer hat die frühere ungültige Variante aufgedeckt und deren Korrektur bestätigt.
- `mail.activity.mixin` löscht beim Archivieren standardmäßig Aktivitäten. Für Anforderungen sind beide Löschwege gezielt neutralisiert; manuelles Erledigen bleibt möglich. Siehe D007.
- Quelle-Viewer speichert nur die Anforderungsreferenz, keinen Snapshottext. Die Quellenanzeige verwendet immer neu berechnetes autorisiertes HTML. Mergeprovenienz wird nur bei Leserecht auf das Herkunfts-REQ ausgegeben.
- Ticketaktionen sind native `ir.actions.server`-Bindings. Noch keine echte Helpdesk-View geerbt. Official Odoo-18-Router bestätigt URLs `/odoo/<model>/<id>` für Modellnamen mit Punkt; Menüs unterstützen SVG-Icons.
- Noch offen: Enterprise/Customs, tatsächliche UI-Darstellung, Odoo.sh-Schutz/Zugriff/Build und neutralisierte Staging-Abnahme. Browserwerkzeug scheiterte bei Initialisierung mit `node:process`-Importfehler. Keine Infrastrukturänderung als Ausweichlösung vorgenommen.
- GitHub-Vertragslauf 39678680433 für Codekandidat `9ef47ad` erfolgreich (1m22s); kein Odoo.sh-Nachweis. Checkout-Release v7.0.1 im offiziellen Repository als aktuell verifiziert, Commit `3d3c42e5aac5ba805825da76410c181273ba90b1`, verwendet Node 24. Workflow nutzt explizites Ubuntu 24.04 statt wanderndem `ubuntu-latest`.
- Folgelauf 39679093289 für `e300220` erfolgreich (1m38s), ohne die vorherigen Runner-/Checkout-Veraltungswarnungen. App-Code bleibt identisch zu `9ef47ad`. Nachfolgende reine Dokumentationscommits ändern den geprüften Code nicht und sind per Workflow-Pfadfilter von erneuten Tests ausgenommen. Userdiff `codex-task.md` bleibt unberührt.

## Naming-/Versionsauftrag, 22.10.2026

- Sichtbarer Name jetzt **Anforderungen**, technischer Name `gc_requirements`, vorhandene XML-IDs/Modelle/Felder unverändert. Primärplattform 18, vollständige Unterstützung von 20 als zusätzliches Ziel. Quellenfreigabe gilt unverändert je exaktem aktuellen Ticket.
- Native deutsche Beschriftungen und `i18n/de.po`; Katalog ergänzt auch geerbte Aktivitäts-/Nachrichten-/Metadatenlabels, nicht benutzergepflegte Seeds. Keine neue Einstellungs-/Datenstruktur. Defaultnamen werden beim XML-Upgrade erneut angewendet; dauerhafte Umbenennung als zusammenhängende Manifest-/XML-/Übersetzungsänderung.
- 20er API-Befunde/Branchstrategie/Migrationsgate: `docs/COMPATIBILITY.md`. Separater Development-Port statt Versionsswitches in Sicherheitscode; vorhandene Tests nicht abschwächen.
- `scripts/migration_audit.py` ist nur ein administrativer, lesender Shellprüfer außerhalb des Addons. Inventur mit IDs/Hashes vertraulich und außerhalb Git halten. Er ersetzt keine Datenbankmigration. `test_contract.py --baseline-ref <commit>` prüft zusätzlich das echte Modulupgrade vom vorherigen Git-Code.
- Vollständige 18->20-Datenmigration und Enterprise-Prüfungen erfordern genehmigten isolierten Zugang; derzeit nicht vorhanden. Keine Staging-/Production-Freigabe ableiten.

- Odoo 20 verwendet `ir.access`, effektive `all_group_ids`, native Constraint-/Domain-/Gruppierungs-APIs, `raw.content` und typisierte Testparameter. Für strukturiertes Chatter-Tracking ist das offizielle zusätzliche `mail_tracking` erforderlich. Der Port darf die Historieninventur nicht auf reinen Nachrichtentext reduzieren.

- Finaler Vertrag 22.10.2026: 18 frisch 27/27, alter Kandidat 26/26, Upgrade 27/27; 20 frisch 27 App + 2 Web, Upgrade 27 App, beide Inventuren/negative Proben bestanden. SQL-Zählerlesen 18 nach Upgrade 13, 20 5 Abfragen. Keine Enterprise-/Odoo.sh-/Major-Migrationsabnahme.

- Für eine echte strukturierte Historien-Fixture erst die Erstellung committen, danach Priorität/Zuweisung ändern und `_track_finalize()` ausführen; im Erstellungs-Transaktionskontext unterdrückt Odoo Tracking. Die Fixture verlangt jetzt ausdrücklich vorhandene Trackingzeilen, bevor sie die Upgradeinventur speichert.

- Aktueller Rechner: Origin HTTPS lesbar, Push ohne Anmeldung nicht möglich. SSH hat keinen bestätigten GitHub-Hostschlüssel; nicht automatisch einrichten/umgehen. Neue Commits lokal halten, bis ein autorisierter sicher konfigurierter GitHub-Zugang verfügbar ist.


## Releaseplanung / Worktimes, 22.10.2026

- Auftrag `tasks/20261022_releases-milestones.md`, SPEC §14, Entscheidung D019. Neue Version 18.0.1.3.0 / 20.0.1.3.0. Modell `gc.requirement.milestone`, Referenz `MS-####`, optionale kanonische `milestone_id`, `worktimes_url`; keine Änderung tatsächlicher Veröffentlichung oder Requirementstatus durch Planung.
- `assignment_ids` ist berechnete inverse Many2many-Auswahl vorhandener Requirements über die eine FK-Beziehung, keine weitere Persistenz. Produktwechsel beider Richtungen prüfen, auch archivierte. Acht aktive Statuszähler, Archiv separat, zurückgestellt offen, Abgelehnt aus Fortschrittsnenner entfernt. Aktuelle Benutzerrechte ohne sudo.
- Gemeinsamer `internal_chatter.py` vor Requirement importieren; Mixin erbt selbst mail.thread/activity. Eine spätere zusätzliche Mixin-Vererbung kann MRO brechen oder core message_post Vorrang geben. Vollständige bestehende Follower-/Nachrichten-Suite muss weiterlaufen.
- Abschlusswizard mit Pflichtbestätigung bei aktuellen offenen Anforderungen; privater Prozess-Identitätstoken schützt vor gefälschtem RPC-Kontext. Kein Autoabschluss/keine Ticketnotizen; Entscheidung mit Zählern im Chatter. Archivierung erhält Aktivitäten.
- Im 18er Hauptcheckout lokale Demo: einmalige additive sechs Pläne/zwölf neue Requirements, alle Produkte, produktübergreifend, veröffentlicht mit offenen Anforderungen. Bestehende UI-Daten werden nicht überschrieben. Schema/Views zuerst via `dev.py update` aktualisieren.
- Ruff/uvx hier nicht im PATH: Ruff 0.14.0 isoliert unter `/tmp/gc-release-tools/bin/ruff` installiert; kein Produktdependency.

- Native Odoo-20-`read_group` gibt bei Many2one-Gruppierung IDs zurück, 18er `_read_group` Recordsets. Portzähler verwenden IDs; Constraint/ir.access/all_group_ids und `_notify_get_recipients(message, **kwargs)` bleiben 20-spezifisch. Altvertrag 18 42/32/42 und 20 44/34/42 erfolgreich; Enterprise-/Majorupgrade-/20er Browsernachweise offen.
- Alle drei 18er Browsersuiten bestanden. PriorityField spart nicht nur manuelles Speichern, sondern speichert nativ sofort beim Sternklick; Smoke wartet explizit auf web_save statt gegen den verschwindenden Savebutton zu klicken. Nur Test korrigiert. Neuer Planungssmoke verwendet echten Many2many-Auswahldialog und die native Liste für Detailnavigation.

- Releaseplanung final lokal: 18 `e43cab7` + `0b71c26`, 20 `7213606`. Auch die letzte XML-Dialogänderung in beiden normalen Verträgen mit 42/42 beziehungsweise 44/42 Tests und vollständiger Erhaltungsinventur/Negativproben geprüft; Planungssmoke danach erneut bestanden. Beide Pushes Exit 128 wegen fehlender GitHub-HTTPS-Anmeldung. Reine Abschlussdokumentation folgt in Git; keine neue CI-/Odoo.sh-Beobachtung. Nur die eigene lokale UI bleibt aktiv, synthetische Teststacks durch Testtreiber entfernt.
