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

`docker compose -p gc-req-dev -f compose.test.yaml up -d db`

`docker compose -p gc-req-dev -f compose.test.yaml run --rm odoo`

Odoo-Image `odoo:18.0`, Digest `sha256:1b346c6f9145c79b802b711a554a141acbd0503ed6cd7d31cb3c938889c4cc36`, PostgreSQL 15. Ausschließlich synthetische Daten, keine veröffentlichten Ports. `tests/contract_addons/helpdesk` ist ein expliziter Testvertrag, KEIN Enterprise-Modul und darf niemals auf dem produktiven Addonspfad stehen. Nur `addons/` deployen.

M1: Installation und 4 Tests nach Korrektur zweier Test-Exception-Erwartungen erfolgreich; `0 failed, 0 error(s)`. Python-Kompilierung und XML-Syntaxprüfung erfolgreich. Die Odoo-18-Laufzeit bestätigt `_has_cycle()` statt des veralteten `_check_recursion()`.

M2: 7 Tests, `0 failed, 0 error(s)`, einschließlich Pflichtbegründungen über direkten ORM-Zugriff, Wizard, Follower-Abweisung und manueller Aktivität. Testbenutzer verwenden anschließend `no_reset_password=True`; Test-Signup-Benachrichtigungen sind nicht Bestandteil des App-Verhaltens.

M3: 17 Tests, `0 failed, 0 error(s)` nach Korrektur des ersten Laufs. Exportprivileg für Support-Testbenutzer explizit gesetzt. Direkte rohe `read/search_read/read_group/export/search_count`-Versuche verweigert; eigener Ticket-Record-Rule-Entzug greift auch beim bestehenden Viewer. Statusnotiztest: sechs interne Notizen für zwei Tickets/drei tatsächliche Übergänge, keine zusätzlichen `mail.mail`/`mail.notification`, keine Ticketstatus-/Prioritätsänderung und keine Aktivitäten im synthetischen Vertrag.

M4: 21 Tests, `0 failed, 0 error(s)`. Originalaktivitäten, Anhänge und Historie nach Merge erhalten; überlappende Snapshots getrennt erhalten; unerlaubte/selbstbezügliche/unbestätigte/erneute Merges und direkte Redirects abgewiesen. Odoo-Aktivitätslöschung beim Archivieren gezielt unterbunden und manuelles Erledigen danach getestet.

## Zielinstallation (noch nicht ausgeführt)

Addon-Verzeichnis `addons` auf den Odoo-Addonspfad setzen; Odoo 18 Enterprise mit `mail` und `helpdesk` bereitstellen. Nur isolierte Development-Datenbank verwenden. Installation: `odoo --stop-after-init -d <development-db> -i gc_requirements --test-enable --test-tags /gc_requirements`. Upgrade entsprechend mit `-u gc_requirements`. Platzhalter sind bewusst keine existierenden Datenbanknamen.

Odoo.sh: Projekt und Development-Zuordnung sowie technische Zugriffsbeschränkungen erst bestätigen. GitHub-Branch allein belegt keine sichere Odoo.sh-Konfiguration. Staging benötigt frische Kandidatenfreigabe und neutralisierte Mail-/Integrationsumgebung, Production eine separate Freigabe.
