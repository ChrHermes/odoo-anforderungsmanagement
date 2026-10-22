# Installations- und Testhandbuch

## Persistente lokale Browserumgebung (22.10.2026)

Anleitung: [LOCAL_DEVELOPMENT](LOCAL_DEVELOPMENT.md). `python3 scripts/dev.py start` installiert/startet ausschließlich den eigenen UI-Stack; `credentials`, `status`, `stop`, `update`, `reset --yes`, `logs`, `test` und `verify` sind die lokalen Betriebsbefehle. `compose.test.yaml` und der bestehende Testtreiber bleiben unverändert. Ausschließlich synthetische Daten; derzeit gekennzeichnete UI-Demo, Enterprise-Zugriff weiter HTTP 404.

Tatsächlich ausgeführt: frischer Dev-Install, Seed und Neutralisierungs-/Zugriffsprüfung; `python3 scripts/dev.py test` mit **27/27** Tests nach Install, **27/27** nach Upgrade und erfolgreicher Vorher-/Nachher-Inventur samt negativen Proben. Contract-Cleanup beendet nur seinen Stack, die UI läuft weiter. `python3 scripts/dev.py update` führt ein echtes Modulupgrade der bereits im Browser benutzten Entwicklungsdatenbank erfolgreich aus.

Zusätzlich ausgeführt: `python3 scripts/dev.py stop` gefolgt von `start`. Anschließender Browser-/Benutzer-RPC-Check bestätigt unveränderte Referenz, bearbeiteten Titel, Prüfstatus, drei Sterne, manuelle Aktivität, interne Notiz und Ticketmomentaufnahme aus der interaktiven Erfassung. `reset --yes` gefolgt von `start` entfernt/reproduziert ausschließlich diesen lokalen Stack samt seinen beiden Volumes; frische Installation/Seed und anschließender vollständiger Browsercheck erneut bestanden. Der Reset ohne `--yes` wurde erwartungsgemäß verweigert. Login-Ausgabebefehl mit unterdrückter Geheimnisausgabe geprüft; kein globales Docker-Cleanup.

Playwright-/Chromium-Browserprüfung tatsächlich bestanden: Anmeldung/Kachel, native Kanban- und Listenansicht, manuelles Erstellen mit eigener Beschreibung/Produkt/Kategorie/drei Sternen, Bearbeiten, Statuswizard, interne Notiz, manuelle Aktivität, synthetischer Ticketwizard und autorisierter Quellenviewer. Keine JavaScriptfehler oder externen Browserrequests. Screenshots in `.local/dev/browser/` werden zusätzlich visuell betrachtet. **Kein Ersatz für Enterprise-Helpdesk-UI und echte Custom-Record-Rules.**

Docker-Portprüfung bestätigt `HostIp=127.0.0.1`, `HostPort=8069`; HTTP-Login liefert 200. Odoo hat nur das interne Netz, keinen Gateway und keine veröffentlichten Hostports. Externe Socketprobe scheitert erwartungsgemäß mit `Network is unreachable`. Startkonfiguration/Verifier bestätigen Cronthreads 0, deaktivierte Cron-/Mailserver und SMTP-Loopbackport 1. Watchdog für Python-Autoreload im Startlog bestätigt.

Vorläufe fanden einen fehlenden synthetischen Chatter-Absender und den Odoo-Core-Fehler in `--dev=xml`; beides im lokalen Umfeld behoben (gültige `example.invalid`-Adresse und `reload,qweb`). Browserselektoren auf beobachtete deutsche Labels/Selectionwerte angepasst; finaler Smokecheck vollständig bestanden. Globale `git diff --check` meldet vorhandene fremde CRLF-Diffs; nur eigene/staged Änderungen separat auf Whitespace prüfen, keine fremden Dateien normalisieren.

Kandidat `95880cd` lokal committed. Development-Push mit `GIT_TERMINAL_PROMPT=0 git push origin HEAD:refs/heads/codex/initial-mvp` tatsächlich versucht, Exit 128 mangels HTTPS-Benutzeranmeldung. Nicht gepusht, kein neuer CI-/Odoo.sh-Build beobachtet. Nach autorisierter Einrichtung des GitHub-Zugangs denselben Befehl wiederholen. Lokale UI bleibt davon unabhängig aktiv.

## Wiederaufnahme

`docs/STATUS.md`, `PROJECT_MEMORY.md`, `DECISIONS.md`, `DEVELOPMENT_REPORT.md` und anschließend Spezifikationen lesen. `git status --short --branch`, `git log -8 --oneline`, `git remote -v` prüfen. Development-Arbeit nur auf `codex/initial-mvp` (18) und dem separat beauftragten `codex/20.0-port` (20). Keine lokalen Nutzerdiffs überschreiben.

## Bereits ausgeführte Prüfungen

- `git status --short --branch`, `git log -6 --oneline`, `git remote -v`: erfolgreich.
- `GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND='ssh -o BatchMode=yes -o ConnectTimeout=10' git ls-remote --heads origin`: erfolgreich.
- `docker info --format '{{.ServerVersion}}'`: Docker 29.4.2 verfügbar.
- Python-Importprüfung: kein lokales `odoo`, `lxml`, `psycopg2`, `pytest`.
- `gh api repos/odoo/enterprise`: 404, kein nutzbarer Enterprise-Zugriff.

## Isolierter Community-Vertrag (ausgeführt)

Aktueller Einstieg auf einem neuen Rechner: **`python3 scripts/test_contract.py`**. Er führt Syntax/Paketprüfung, frische Installation mit 27 Tests, Aufbau einer persistenten synthetischen Upgrade-Fixture, echtes `-u gc_requirements` mit 27 Tests und Erhaltungsnachweise aus. Anschließend entfernt er nur sein eigenes Compose-Projekt `gc-requirements-contract` samt Testvolume. `--keep` lässt es stehen; ein Folgelauf setzt ausschließlich diesen Teststack zurück. Docker-Images sind per Digest fixiert, Testnetz intern, keine Hostports. Ergebnisse werden in `.local/test-results/` geschrieben und nicht versioniert.

`python3 scripts/check_static.py` läuft ohne externe Python-Pakete. Optional: `uvx ruff check addons scripts tests` und `uvx ruff format --check addons scripts tests` mit der Repository-Konfiguration `ruff.toml`; beides ausgeführt und bestanden. Die früheren direkten `gc-req-dev`-Befehle unten dokumentieren den Entwicklungsverlauf.

`docker compose -p gc-req-dev -f compose.test.yaml up -d db`

`docker compose -p gc-req-dev -f compose.test.yaml run --rm odoo`

Odoo-Image `odoo:18.0`, Digest `sha256:1b346c6f9145c79b802b711a554a141acbd0503ed6cd7d31cb3c938889c4cc36`, PostgreSQL 15. Ausschließlich synthetische Daten, keine veröffentlichten Ports. `tests/contract_addons/helpdesk` ist ein expliziter Testvertrag, KEIN Enterprise-Modul und darf niemals auf dem produktiven Addonspfad stehen. Nur `addons/` deployen.

M1: Installation und 4 Tests nach Korrektur zweier Test-Exception-Erwartungen erfolgreich; `0 failed, 0 error(s)`. Python-Kompilierung und XML-Syntaxprüfung erfolgreich. Die Odoo-18-Laufzeit bestätigt `_has_cycle()` statt des veralteten `_check_recursion()`.

M2: 7 Tests, `0 failed, 0 error(s)`, einschließlich Pflichtbegründungen über direkten ORM-Zugriff, Wizard, Follower-Abweisung und manueller Aktivität. Testbenutzer verwenden anschließend `no_reset_password=True`; Test-Signup-Benachrichtigungen sind nicht Bestandteil des App-Verhaltens.

M3: 17 Tests, `0 failed, 0 error(s)` nach Korrektur des ersten Laufs. Exportprivileg für Support-Testbenutzer explizit gesetzt. Direkte rohe `read/search_read/read_group/export/search_count`-Versuche verweigert; eigener Ticket-Record-Rule-Entzug greift auch beim bestehenden Viewer. Statusnotiztest: sechs interne Notizen für zwei Tickets/drei tatsächliche Übergänge, keine zusätzlichen `mail.mail`/`mail.notification`, keine Ticketstatus-/Prioritätsänderung und keine Aktivitäten im synthetischen Vertrag.

M4: 21 Tests, `0 failed, 0 error(s)`. Originalaktivitäten, Anhänge und Historie nach Merge erhalten; überlappende Snapshots getrennt erhalten; unerlaubte/selbstbezügliche/unbestätigte/erneute Merges und direkte Redirects abgewiesen. Odoo-Aktivitätslöschung beim Archivieren gezielt unterbunden und manuelles Erledigen danach getestet.

M5 final: Odoo **18.0-20261015**, frischer Install **26/26**, Upgrade **26/26**, jeweils `0 failed, 0 error(s)`; `CONTRACT_UPGRADE_VERIFIED` für Seeds, Referenz, Snapshot und physischen Filestore-Anhang. Kaltes Zählerlesen: 1.000 Anforderungen/2.000 unterschiedlichen Tickets und Quellen in 13 SQL-Abfragen. Native `Form`-Erfassung, Wizarddefaults, Gruppierung und Nummernsuche geprüft. Vorherige M5-Negativtests deckten eine ungültige False-Domain sowie fehlende readonly Pflichtfelddefaults auf; beides korrigiert und vollständig erneut geprüft.

Bekannte nicht blockierende Laufzeitdiagnostik: Odoo meldet für das absichtlich private Quellmodell fehlende ACLs; **keine lesende ACL ergänzen**. Das unveränderte Standardmodul `mail` im gepinnten Image gibt beim frischen Install zwei Docutils-/RST-Diagnosen aus. Installation und Tests enden dennoch erfolgreich. Eigene XML-Alert-Rollen korrigiert. Visuelle Browserprüfung nicht ausführbar (Browserinitialisierung: `node:process`-Import verweigert).

## Zielinstallation (noch nicht ausgeführt)

Addon-Verzeichnis `addons` auf den Odoo-Addonspfad setzen; Odoo 18 Enterprise mit `mail` und `helpdesk` bereitstellen. Nur isolierte Development-Datenbank verwenden. Installation: `odoo --stop-after-init -d <development-db> -i gc_requirements --test-enable --test-tags /gc_requirements`. Upgrade entsprechend mit `-u gc_requirements`. Platzhalter sind bewusst keine existierenden Datenbanknamen.

Odoo.sh: Projekt und Development-Zuordnung sowie technische Zugriffsbeschränkungen erst bestätigen. GitHub-Branch allein belegt keine sichere Odoo.sh-Konfiguration. Staging benötigt frische Kandidatenfreigabe und neutralisierte Mail-/Integrationsumgebung, Production eine separate Freigabe.

## GitHub-Nachweise (ausgeführt)

`gh run view 39679093289 --repo ChrHermes/odoo-anforderungsmanagement --json status,conclusion,url,headSha` bestätigt Erfolg für `e300220`. Der vorangegangene Lauf 39678680433 bestätigt den App-Codekandidaten `9ef47ad`; beide sind Community-Vertragsprüfungen, keine Enterprise-Builds. GitHub-Logs enthalten die gleichen Install-/Upgrade-/Erhaltungsmarker und 26/26 Tests. Bei gesperrtem lokalem CLI-Logcache kann der lesende Job-API-Endpunkt verwendet werden: `gh api --allow-escape-sequences repos/ChrHermes/odoo-anforderungsmanagement/actions/jobs/119496559137/logs`. Terminal-Steuerzeichen gegebenenfalls nur in eine lokale Logdatei umleiten.

## Manuelle Enterprise-Abnahme (ausstehend)

1. Frisches Development mit synthetischen Tickets installieren/aktualisieren; Module und Custom-Views prüfen. Nur benannte interne Testbenutzer als Pilot aktivieren.
2. Ticketaktion verwenden: eigene redaktionelle Beschreibung, unabhängige Priorität, n:m-Verknüpfung, spätere Ticketbeschreibung ändern. Momentaufnahme bleibt gleich.
3. Zwei App-Benutzer mit unterschiedlichen **tatsächlichen** Ticketrechten verwenden. Quellenviewer/Smart Buttons und direkte ORM/RPC-/Exportwege prüfen; Recht nach bereits geöffnetem Viewer entziehen. Company-/Team-/Custom-Feldregeln einbeziehen.
4. Mail-/Integrationsisolation bestätigen, bevor Status-/Chatter-/Activity-Aktionen ausgeführt werden. Bei Geplant/Umgesetzt/Abgelehnt nur interne Notizen, keine Kundenmails, keine Wiederöffnung, keine Autoaktivität. Auch benutzerdefinierte Automationen auf `mail.message` kontrollieren.
5. Alle nativen Ansichten, Formulare, Filter/Favoriten, Follower/Mentions und Aktivitätsübersicht prüfen. Merge mit überschneidenden Tickets und Anhängen bestätigen; archivierte Originale einschließlich Aktivitäten bleiben erreichbar.
6. Ergebnisse zu einem konkreten Commit unter `docs/ACCEPTANCE.md` dokumentieren. M3-/M5-Gates erst mit realen Nachweisen schließen. Vor Staging frische Businessfreigabe, vor Production separate Freigabe und benannten Pilot einholen.

## Ergänzung Naming / Versionen, 22.10.2026

`python3 scripts/test_contract.py --baseline-ref 36085f50b66102a85515fd004abae59120848af1` prüft den aktuellen frischen Install, installiert danach den alten Git-Kandidaten in einem neu erzeugten synthetischen Stack und aktualisiert ihn auf den Checkout. Git-Baseline muss lokal verfügbar sein. Der Treiber erzeugt sie nur in `.local/baseline`, ändert keinen Branch und entfernt ausschließlich seinen Vertragsstack.

Der erweiterte Erhaltungstest nutzt `scripts/migration_audit.py`, einschließlich archivierter Mergeoriginale, Quellen-/Ticketdaten, Chatter/Tracking, manueller Aktivitäten, physischer Anhänge und effektiver Rechte. Absichtliche Änderungen an Titel/Anhang müssen fehlschlagen und werden per Savepoint zurückgerollt. Deutscher Locale-Test lädt den echten PO-Katalog. Für 20 den separaten Development-Port und dessen Teststack verwenden.

Der administratorseitige Major-Upgrade-Ablauf ist unter [COMPATIBILITY](COMPATIBILITY.md) dokumentiert; **noch nicht ausgeführt**. `capture`/`verify` können in einer autorisierten Odoo-Shell geladen werden; keine Shell-/RPC-Funktion innerhalb des Addons, kein Datenexport in Git. Auf einem neuen Rechner zuerst Git- und Runtimeversionen live prüfen.

Ausgeführt am 22.10.2026 auf Odoo 18.0-20261015: Neuinstallation 27/27, alter Kandidat 26/26, Upgrade auf 18.0.1.1.0 mit 27/27, Inventur inklusive Tracking/Ticketdaten und negative Korruptionsproben bestanden; automatisches Cleanup erfolgreich. `python3 scripts/check_static.py`, Ruff 0.14.0 (`check` und `format --check`) erfolgreich. Enterprise und Major-Migration nicht ausgeführt.

Der Inventurprüfer normalisiert Odoo-18-ACLs/Rules und das beobachtete Odoo-20-`ir.access` zu vergleichbaren Policydefinitionen. Native Sicherheitsdatensätze dürfen intern neue Coremodell-/Zeilen-IDs haben; bestehende XML-IDs und alle fachlichen Ziele müssen erhalten sein. Neue XML-IDs (z. B. der 20er Gruppenscope) sind erlaubt. Reale Policy-/Rechteänderungen führen weiter zum Fehler. Der Treiber verweigert eine `--baseline-ref` mit anderer Majorversion vor jeder Dockeraktion; im 20er Worktree mit `287f078` geprüft (erwarteter Exit 2).

Odoo 20 am 22.10.2026 im separaten Worktree ausgeführt: `python3 scripts/test_contract.py --keep` mit 29 Tests nach Install (27 App, 2 Web), 27 nach Upgrade und positivem Erhaltungsmarker. PostgreSQL 17 statt 15, eigener Compose-Projektname `gc-requirements-contract-20`, Image-Digests im Branch-Compose. Zusätzliche offizielle Abhängigkeit `mail_tracking`. Alle bisherigen Tests behalten, nur native API-Aufrufe angepasst. Nach abschließender Kontrolle wurde ausschließlich der synthetische 20er Stack entfernt. Enterprise und Major-Migration weiterhin nicht ausgeführt.

Git am 22.10.2026: `git push origin HEAD:refs/heads/codex/initial-mvp` scheitert ohne HTTPS-Anmeldung; lesender SSH-Versuch mit `BatchMode=yes`/`StrictHostKeyChecking=yes` scheitert am fehlenden Hostschlüssel. Kein erfolgreicher Push und kein aktueller Remote-Build. Erst sicher eingerichteten Zugang bereitstellen; keine Hostschlüsselprüfung abschalten.
