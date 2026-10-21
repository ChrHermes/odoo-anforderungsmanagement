# Installations- und Testhandbuch

## Wiederaufnahme

`docs/STATUS.md`, `PROJECT_MEMORY.md`, `DECISIONS.md`, `DEVELOPMENT_REPORT.md` und anschließend Spezifikationen lesen. `git status --short --branch`, `git log -8 --oneline`, `git remote -v` prüfen. Ausschließlich `codex/initial-mvp` ändern. Keine lokalen Nutzerdiffs überschreiben.

## Bereits ausgeführte Prüfungen

- `git status --short --branch`, `git log -6 --oneline`, `git remote -v`: erfolgreich.
- `GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND='ssh -o BatchMode=yes -o ConnectTimeout=10' git ls-remote --heads origin`: erfolgreich.
- `docker info --format '{{.ServerVersion}}'`: Docker 29.4.2 verfügbar.
- Python-Importprüfung: kein lokales `odoo`, `lxml`, `psycopg2`, `pytest`.
- `gh api repos/odoo/enterprise`: 404, kein nutzbarer Enterprise-Zugriff.

## Isolierter Community-Vertrag (ausgeführt)

Aktueller Einstieg auf einem neuen Rechner: **`python3 scripts/test_contract.py`**. Er führt Syntax/Paketprüfung, frische Installation mit 26 Tests, Aufbau einer persistenten synthetischen Upgrade-Fixture, echtes `-u gc_requirements` mit 26 Tests und Erhaltungsnachweise aus. Anschließend entfernt er nur sein eigenes Compose-Projekt `gc-requirements-contract` samt Testvolume. `--keep` lässt es stehen; ein Folgelauf setzt ausschließlich diesen Teststack zurück. Docker-Images sind per Digest fixiert, Testnetz intern, keine Hostports. Ergebnisse werden in `.local/test-results/` geschrieben und nicht versioniert.

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
