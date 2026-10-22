# Odoo 18 lokal ausprobieren und entwickeln

Diese Umgebung läuft dauerhaft im Hintergrund auf **http://localhost:8069**. Sie hat eine eigene PostgreSQL-Datenbank und einen persistenten Filestore. `stop` erhält Ihre Änderungen; nur `reset --yes` löscht die lokalen Entwicklungsdaten.

**Aktueller Modus: eingeschränkte UI-Demo mit synthetischem Helpdesk.** Lizenzierter Enterprise-Zugriff war am 22.10.2026 nicht verfügbar (`odoo/enterprise`: HTTP 404, keine lokal bereitgestellten Quellen gefunden). Diese Demo ist keine Odoo-Enterprise-Abnahme. Anmeldung, Kacheleinstieg und Webclient zeigen die Einschränkung an. Enterprise-/Custom-Helpdesk-Rechte und Benachrichtigungsautomationen bleiben gesondert zu prüfen.

## Einmalig vorbereiten

Benötigt werden Git, Python **3.10 oder neuer** und ein gestartetes Docker mit **Compose v2**. Für die normale Anwendung sind weder Node.js noch zusätzliche Python-Pakete erforderlich. Die drei offiziellen Images werden beim ersten Start heruntergeladen und sind per Digest fixiert: Odoo 18.0-20261015, PostgreSQL 15 und Nginx 1.28. Internet ist für diesen Download nötig; der laufende Odoo-/Datenbankstack hat keinen externen Netzpfad.

Im Repository auf dem freigegebenen Branch `codex/initial-mvp` arbeiten:

```sh
git branch --show-current
python3 scripts/dev.py start
python3 scripts/dev.py credentials
```

Der erste Start installiert `gc_requirements` in **`gc_requirements_dev`**, lädt Deutsch und erzeugt die Beispieldaten. Warten Sie auf „Bereit“. Danach **http://localhost:8069/local-dev** öffnen und mit dem angezeigten Konto anmelden. Die Kachel **Anforderungen** öffnet das native Kanban-Board. Die Community-Ausgabe hat keinen Enterprise-Startbildschirm; der kleine lokale Kacheleinstieg gehört ausschließlich zur Entwicklungshilfe.

Das benannte Entwicklungskonto besitzt App-, Konfigurations- und Helpdesk-Benutzerrechte, keine Systemadministrationsrechte. Zufällige lokale Passwörter werden ausschließlich in der ignorierten Datei `.local/dev/credentials.json` erzeugt. Auch Datenbank-, Master- und Administratorpasswort sind zufällig. Keine echten Kunden- oder Zugangsdaten eintragen. `.local/dev/` nur dem eigenen Hostkonto zugänglich halten; auf Windows gegebenenfalls die NTFS-Berechtigungen prüfen.

## Bedienung

- **Kanban / Liste:** oben rechts umschalten; die Kanban-Spalten bei Bedarf horizontal scrollen.
- **Neu:** Titel, Typ, Produkt und redaktionelle Beschreibung eingeben. Optional einen Funktionsbereich und Priorität mit 0–3 Sternen wählen. Oben mit dem Speichersymbol sichern.
- **Status ändern:** öffnet den Statusdialog. Zurückgestellt und Abgelehnt verlangen eine Begründung. Umgesetzt bedeutet veröffentlicht; das Veröffentlichungsdatum und die Version können erfasst werden.
- **Konfiguration:** Produkte und Funktionsbereiche bearbeiten; die getrennten BASE-Äste bleiben eigenständige Einträge.
- **Produktfarben:** unter Konfiguration → Produkte das Produkt öffnen. Der native Farbwähler und das Hex-Textfeld bearbeiten denselben Wert (`#RRGGBB`). Nur Konfigurationsbenutzer dürfen ändern; eigene Farben bleiben bei Modulupgrades erhalten. Nexus und Allgemeines haben keine vorgeschlagenen Unterbereiche.
- **Chatter:** interne Notiz hinterlassen; über Aktivitäten eine manuelle Aufgabe planen. Testmails werden nicht zugestellt.
- **Kunden & Tickets:** „Ursprüngliche Ticketbeschreibungen anzeigen“ öffnet pro berechtigt lesbarem Ticket dessen Nummer, Titel, Kunde, Capture-Provenienz und unveränderliche Original-Momentaufnahme. Ohne Ticket steht dort „Keine Helpdesk-Tickets verknüpft“. Der vollständige aktuelle Verlauf bleibt über den Ticketlink im Helpdesk.
- **Helpdesk (UI-Demo):** über den Kacheleinstieg öffnen. Im geöffneten Ticket das Zahnrad-/Aktionenmenü und „Anforderung erstellen/verknüpfen“ verwenden. „Verknüpfte Anforderungen“ führt zurück. Dies ist nur der synthetische Vertrag; echte Enterprise-Teams/Regeln/Ansichten werden damit nicht nachgebildet.

Die ursprünglichen Fixtures enthalten acht synthetische Anforderungen in allen acht Status und allen vier Prioritäten, drei Tickets, zwei Kontakte derselben Beispielorganisation, einen weiteren Beispielkunden, getrennte Redaktion/Quellen, eine interne Notiz und eine manuell angelegte Beispielaktivität. Die Seeds werden nur einmal angelegt; wiederholtes Starten überschreibt keine bearbeiteten Beispieldaten.

Seit dem UX-Update enthält die App fünf Installationsprodukte (zusätzlich Nexus und Allgemeines), weiterhin 15 Bereiche sowie zwei zusätzliche lokale Anforderungsbeispiele ohne Bereich/Ticket. Die ursprüngliche Messgeräte-Anforderung hat zwei verknüpfte Beispiel-Tickets mit nichtleeren Quellen. Ein zweiter interner Demo-Benutzer **ohne Helpdesk-/Config-Rechte** ermöglicht den negativen Viewer-/API-/Exportfall. Dessen Zugang: `python3 scripts/dev.py credentials --restricted`. Alle Konten sind ausschließlich lokal erzeugt, Passwörter bleiben in `.local/dev/credentials.json`. `update`/`start` ergänzen nur fehlende verwaltete Demo-Fixtures, ohne vorhandene Anforderungen oder Momentaufnahmen zu überschreiben.

## Die wichtigsten Befehle

Alle Befehle im Repository ausführen:

| Zweck | Befehl |
|---|---|
| Starten / nach Docker-Neustart prüfen | `python3 scripts/dev.py start` |
| Beenden, Daten behalten | `python3 scripts/dev.py stop` |
| Modul und Ansichten aktualisieren | `python3 scripts/dev.py update` |
| Containerzustand anzeigen | `python3 scripts/dev.py status` |
| Odoo-Logs verfolgen, Ende mit Strg+C | `python3 scripts/dev.py logs` |
| Lokalen Login anzeigen | `python3 scripts/dev.py credentials` |
| Installation, Pilotzugriff und Neutralisierung prüfen | `python3 scripts/dev.py verify` |
| Bestehende isolierte Install-/Upgrade-Tests | `python3 scripts/dev.py test` |
| Ausschließlich lokale UI-Daten **löschen** | `python3 scripts/dev.py reset --yes` |
| Nach dem Reset neu installieren | `python3 scripts/dev.py start` |

Das Compose-Projekt heißt fest **`gc-requirements-dev`**. Seine Volumes **`gc-requirements-dev_postgres-data`** und **`gc-requirements-dev_odoo-data`** speichern Datenbank und Filestore einschließlich Anhängen. `restart: unless-stopped` startet die Dienste beim Docker-Neustart wieder, solange sie nicht ausdrücklich gestoppt wurden. Docker Desktop selbst muss laufen.

Der Reset entfernt ausschließlich Container, Netzwerke und Volumes dieses Projekts. Lokale Zugangsdaten und Diagnose-/Browserdateien bleiben erhalten. Nie globale Docker-Prune-Befehle verwenden. Der bestehende Vertrag **`gc-requirements-contract`** nutzt weiterhin `compose.test.yaml`, seine eigene Datenbank, seine eigene generierte Helpdesk-Kopie und sein eigenes Cleanup. `dev.py test` führt genau den vorhandenen Testtreiber aus; es testet keinen Enterprise-Helpdesk und setzt die UI-Daten nicht zurück.

## Änderungen entwickeln

`./addons` ist direkt und nur lesbar in Odoo eingebunden. Pythonänderungen sind sofort im Container vorhanden; der bestätigte Watchdog lädt Python mit `--dev=reload,qweb` neu. Neue Felder, Manifest-/Daten-/Ansichtsänderungen benötigen zusätzlich **`python3 scripts/dev.py update`**, anschließend die Browserseite neu laden, bei Assetänderungen gegebenenfalls mit geleertem Cache.

Der Update-Befehl stoppt den Odoo-Webprozess, führt ein echtes `-u gc_requirements,gc_local_dev` aus, prüft die lokale Datenbank und startet die Oberfläche wieder. Schlägt das Upgrade fehl, bleibt der Webprozess gestoppt; Fehler beheben und `update` wiederholen. Die vollständigen Installations-, Seed-, Upgrade- und Prüfprotokolle stehen unter `.local/dev/logs/`.

Bewusst kein `--dev=xml`: Der gepinnte Odoo-18-Core wirft bei vorhandenen gültigen kompakten `<field type="xml"><list>…`-Ansichten im Datei-Lesepfad einen `TypeError` (`NoneType + str`). Normales Laden/Upgrade der Ansichten funktioniert. Der Anwendungsquellcode wurde dafür nicht verändert.

## Lizenzierte Enterprise-Quellen verwenden

Nur ein rechtmäßig bereitgestelltes Checkout der **Odoo-18-Enterprise-Addons** verwenden. Der Pfad muss unter anderem `helpdesk/__manifest__.py` und `web_enterprise/__manifest__.py` enthalten. Die offizielle Helpdesk-Lizenz `OEEL-1` wird geprüft; kurze native Manifestversionen wie `1.0` beweisen keine Odoo-Majorversion. Die Herkunft muss deshalb ausdrücklich Odoo 18 sein. Die vorhandene lokale Berechtigung auf Quellen ist keine automatische Enterprise-Fachabnahme.

Vor dem **ersten** Start, beispielsweise mit einem benachbarten Checkout:

```sh
python3 scripts/dev.py start --mode enterprise --enterprise-path ../enterprise-18
```

Alternativ `GC_ENTERPRISE_PATH` setzen. Relative Pfade werden zum aktuellen Arbeitsverzeichnis aufgelöst und nur in der ignorierten lokalen Zustandsdatei gespeichert. Es gibt keine festen Hostpfade im Repository. Enterprise liegt vor den übrigen Addons auf dem Odoo-Suchpfad und wird nur lesbar eingebunden. Im Enterprise-Modus wird **keine** synthetische Helpdesk-Kopie generiert; es gibt keinen stillen Fallback. Zusätzlich wird `web_enterprise` installiert.

Der Modus ist an die lokale Datenbank gebunden. Ein Wechsel zwischen Demo und Enterprise oder zu einem anderen Quellpfad erfordert zuerst `reset --yes` im bisherigen Modus, dann einen neuen expliziten Start. Damit wird kein synthetisch installiertes Modul über ein echtes Enterprise-Modul aktualisiert. Enterprise-Start/Browserabläufe sind mangels Quellen **noch nicht ausgeführt**; fehlende native Abhängigkeiten oder andere APIs können weitere Anpassungen erfordern. Echte Helpdesk-Aktionen verwenden die vorhandenen nativen Bindings, keine erfundenen View-Anker.

## Netz und Mail

Nur Nginx veröffentlicht **`127.0.0.1:8069`**. Odoo und PostgreSQL sind ausschließlich mit dem internen Netz verbunden, ohne Hostports und ohne Internetroute. Nginx hat ein zweites Netz für den lokalen Browserzugriff und reicht nur an den festen Odoo-Upstream weiter. Das ist kein allgemeiner Forward-Proxy. Diese Trennung ist nötig, weil die hier beobachtete Docker-Version Portweiterleitungen eines ausschließlich internen Netzes nicht am Host bereitstellt.

Cronthreads sind auf 0 gesetzt, vorhandene Cronjobs und ausgehende Mailserver werden beim Start/Update deaktiviert. Der SMTP-Fallback zeigt auf den geschlossenen Container-Loopbackport 1. Datenbankmanager und Datenbankliste sind deaktiviert, der Datenbankfilter erlaubt nur `gc_requirements_dev`. Produktive Volumes, Backups, Dienste, Tokens und Integrationen werden nicht eingebunden. Die Oberfläche ist für die lokale synthetische Entwicklung vorgesehen, nicht für öffentliche Bereitstellung.

## macOS und Windows/WSL2

- **macOS:** Docker Desktop starten und den Checkout für Bind-Mounts freigeben. Python 3 verwenden. Die Images unterstützen die von Docker bereitgestellte Architektur; Apple-Silicon-Ausführung wurde hier nicht geprüft. Kein `platform: linux/amd64` erzwungen.
- **Windows:** Docker Desktop mit WSL2-Backend und Integration für die verwendete Distribution aktivieren. Die Befehle in deren WSL-Shell ausführen. Im Windows-Browser dieselbe URL `http://localhost:8069` öffnen; WSL-Localhostweiterleitung muss aktiviert sein. Die Windows-Browserweiterleitung wurde hier nicht separat visuell geprüft.
- Der Checkout kann unter `/mnt/c/...` liegen; das wurde hier verwendet. Ein Checkout im Linux-Dateisystem ist bei vielen Dateiänderungen oft schneller. Falls ein Bind-Mount keine Änderungsereignisse weitergibt, `update` ausführen; der zuverlässige Neustart/Upgradepfad bleibt vorhanden.
- Port 8069 muss frei sein. Bei einem Konflikt meldet Docker den Fehler; keine anderen Container beenden. Falls Browserzugriff fehlschlägt: `status`, `logs` und die install-/seed-/verify-Protokolle prüfen. Bei abgebrochener Erstinstallation gegebenenfalls ausschließlich diese lokalen Daten mit `reset --yes` neu aufbauen.

### Python scheitert schon beim Import mit `FileNotFoundError`

Ein Traceback bei `import argparse` über `_path_importer_cache` / `_path_abspath` deutet auf einen ungültigen aktuellen Verzeichnisbezug der Shell hin. `ll` kann dabei noch Dateien anzeigen. Derselbe Importfehler wurde mit einem gelöschten Arbeitsverzeichnis reproduziert; das Dev-Skript und seine Zugangsdaten waren im gültigen Repository-Verzeichnis lesbar.

Das Verzeichnis über seinen Namen neu betreten, ohne Testdaten zurückzusetzen:

```sh
gc_repo_dir="$PWD"
cd /
cd "$gc_repo_dir"
python3 scripts/dev.py credentials
```

Falls der gespeicherte Pfad selbst nicht mehr existiert, den Checkout im neuen Terminal über seinen tatsächlichen absoluten Pfad öffnen. Unter WSL kann zusätzlich `/usr/bin/python3 scripts/dev.py credentials` den Systeminterpreter ausdrücklich auswählen. Dafür sind weder ein Docker-Neustart noch ein Datenbankreset erforderlich.

## Automatisierte Browserprüfung

Optional zusätzlich Node.js und Playwright installieren, getrennt vom Produkt und Git-ignoriert:

```sh
npm install --prefix .local/browser --no-audit --no-fund --ignore-scripts playwright@1.56.1
node .local/browser/node_modules/playwright/cli.js install chromium
node scripts/browser_smoke.mjs
```

Auf Linux benötigt Chromium seine Systembibliotheken; Playwright nennt fehlende Pakete beim Start. Auf diesem WSL-Rechner wurden `libnspr4`, `libnss3` und `libasound2t64` ausschließlich lokal entpackt; der tatsächliche Aufruf nutzte:

```sh
LD_LIBRARY_PATH="$PWD/.local/browser/system-libs/root/usr/lib/x86_64-linux-gnu" \
PLAYWRIGHT_BROWSERS_PATH=/tmp/gc-local-browser node scripts/browser_smoke.mjs
```

Der Smokecheck meldet jeden tatsächlich bestandenen Ablauf, scheitert bei Browserfehlern oder externen Browserrequests und legt Screenshots sowie `result.json` unter `.local/dev/browser/` ab. Er erzeugt bewusst einen zusätzlichen synthetischen Anforderungsdatensatz mit Notiz/Aktivität; er löscht keine vorhandenen Daten. Diese Nachweise gelten ausschließlich für die lokale Ausgabe und den dokumentierten Modus. Aktuelle Ergebnisse: [STATUS](STATUS.md), [RUNBOOK](RUNBOOK.md).

Zusätzlicher UX-Check mit derselben Playwright-Installation: `node scripts/browser_ux.mjs` (auf dem beschriebenen WSL-Rechner dieselben `LD_LIBRARY_PATH`-/`PLAYWRIGHT_BROWSERS_PATH`-Variablen setzen). Er prüft fünf exakte Standardfarben, Kontrast, editierbare Hex-Konfiguration mit Wiederherstellung der Ausgangsfarbe, acht Status auch bei leerem Suchergebnis, schmalen Viewport, lesbaren/gesperrten Original-Viewer sowie generische Snapshot-API-Abweisungen. Er erwartet die Standardfarben; auf absichtlich individuell konfigurierten Testdaten die Abweichung fachlich bewerten und keine Nutzerfarben zurücksetzen. Screenshots/Ergebnis: `.local/dev/browser-ux/`, insbesondere `kanban.png`, `kanban-terminal.png`, `kanban-narrow.png`, `product-configuration.png`, `authorized-snapshot.png`, `denied-snapshot.png` und `no-tickets.png`. Manuell dieselben Schritte mit Entwicklungs- und eingeschränktem Konto nachvollziehen; Browserseite nach `update` neu laden.

Referenzen: [offizielle Odoo-18-Quellinstallation und Enterprise-Addonpfad](https://www.odoo.com/documentation/18.0/administration/on_premise/source.html), [Docker-Compose-Netzwerke](https://docs.docker.com/reference/compose-file/networks/), [lokale Portbindung](https://docs.docker.com/engine/network/port-publishing/).


## Releaseplanung: Status manuell ändern

Im Release- oder Meilensteinformular öffnet **Status ändern** die freie Auswahl von Entwurf, Geplant, Aktiv, Abgeschlossen / Veröffentlicht und Abgesagt. Das funktioniert auch ohne Anforderungen. „Veröffentlichen“/„Abschließen“ öffnen denselben Dialog mit vorausgewähltem Abschluss. Bei nicht umgesetzten Anforderungen zeigt der Dialog deren aktuelle lesbare Anzahl einschließlich abgelehnter/archivierter Einträge; Checkbox ausdrücklich bestätigen. Abschlussdatum im Dialog wählen, Standard heute.

Wiederöffnung über denselben Statusdialog erhält das letzte Abschlussdatum. Ein erneuter Abschluss ergänzt eine neue datierte Historiennotiz. Anforderungen behalten ihre Status und tatsächlichen Veröffentlichungsdaten. **Umgesetzte Anforderungen** zeigt „X von Y Anforderungen umgesetzt“ und optional Prozent/Balken: Bezugsmenge aktive Anforderungen ohne Abgelehnte, separat zu Gesamt-/Archivzahlen. 100 % bedeutet keine Veröffentlichung und bildet nicht die gesamte Entwicklungsarbeit ab. Ohne zugeordnete Anforderungen erscheint ein ausdrücklicher Leerhinweis.
