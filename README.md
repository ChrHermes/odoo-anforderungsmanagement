# Anforderungen

Native interne Odoo-App (18 als primäre Plattform, 20 als separates Portierungsziel) `gc_requirements`: Anforderungskatalog, Produkthierarchie, Workflow, Chatter/Aktivitäten, geschützte Helpdesk-Momentaufnahmen und verlustfreie Duplikatzusammenführung. Oberfläche deutsch, Zugriff ausschließlich für ausdrücklich freigeschaltete interne Mitarbeiter.

**Stand:** M1–M5-Code implementiert und im isolierten Odoo-18-Community-Vertrag getestet. Enterprise-/Odoo.sh-/Staging-Abnahme offen. Kein freigegebener Production-Release. [Entwicklungsbericht](DEVELOPMENT_REPORT.md), [aktueller Status](docs/STATUS.md), [Abnahmenachweise](docs/ACCEPTANCE.md).

Versionsnachweise und Branch-/Migrationsstrategie: [COMPATIBILITY](docs/COMPATIBILITY.md). Eine Odoo-20-Portierung und ein Modulupgrade ersetzen keine vollständige Datenbankmigration.

**Dieser Branch:** `codex/20.0-port`, Version `20.0.1.1.0`. Der primäre Odoo-18-Stand liegt auf `codex/initial-mvp`. Nur für Odoo 20 installieren; vollständige Enterprise-/Migrationsabnahme noch offen.

## Installation auf Development

1. Odoo **20 Enterprise** mit installiertem Helpdesk, Mail und dem offiziellen Modul `mail_tracking` bereitstellen. Bestehende Helpdesk-Customizations und deren Record Rules inventarisieren.
2. **Nur `addons/gc_requirements`** auf den Addonspfad deployen. `tests/contract_addons/helpdesk` ist ein synthetischer Testvertrag und darf niemals auf Enterprise/Odoo.sh installiert werden. In Odoo.sh muss das Unterverzeichnis `addons` tatsächlich im Addonspfad gefunden werden; im Buildlog prüfen.
3. App-Liste aktualisieren, **Anforderungen** installieren. Zunächst ausschließlich Development und synthetische Daten verwenden.
4. Benannten internen Pilotmitarbeitern die Gruppe **Anforderungen: Benutzer** geben; Stammdatenadministratoren zusätzlich **Konfiguration**. Helpdesk-Rechte werden separat vergeben und nicht durch die App erweitert.
5. Unter Konfiguration Produkte/Funktionsbereiche prüfen. Die drei Produkte und 15 Kategorien werden bei Installation angelegt; Benutzeränderungen bleiben beim Upgrade erhalten.

Die Ticketaktionen stehen im nativen **Aktionenmenü**: „Anforderung erstellen/verknüpfen“ und „Verknüpfte Anforderungen“. Eine echte Ticketbeschreibung wird erst beim Verknüpfen unveränderlich erfasst. Die redaktionelle Beschreibung muss der Mitarbeiter selbst formulieren. In „Kunden & Tickets“ öffnet „Autorisierte Ticketquellen anzeigen“ nur aktuell erlaubte Quellen.

## Tests auf einem neuen Rechner

Python 3 und Docker mit Compose installieren. Aus dem Repository:

```sh
python3 scripts/check_static.py
python3 scripts/test_contract.py
```

Der zweite Befehl lädt fest versionierte Images, erzeugt ausschließlich eigene synthetische Testdaten in einem isolierten internen Docker-Netz ohne veröffentlichte Ports und prüft frische Installation, ORM/Sicherheit, Upgrade mit bearbeiteten Stammdaten sowie Erhalt von Referenz, Momentaufnahme und Anhang. Er entfernt anschließend ausschließlich den Test-Compose-Stack `gc-requirements-contract`. Das feste Testpasswort gilt nur für dessen wegwerfbare Datenbank. Lokale Logs liegen ignoriert unter `.local/test-results/`. `--keep` lässt diese synthetische Umgebung zur Inspektion bestehen; ein erneuter Lauf setzt sie zurück.

Der versionierte Helpdesk-Testvertrag besitzt nur eine Manifestvorlage und ist für Odoo nicht als Addon erkennbar. Der Testtreiber erzeugt das Testmodul ausschließlich unter `.local/contract-addons/` (Git-ignoriert), damit es beim Deployment keine Enterprise-Module überschattet. Compose direkt erst nach dieser Vorbereitung verwenden.

Lizenzierte Enterprise-Prüfung in einer isolierten Development-Installation (Platzhalter ersetzen):

```sh
odoo --addons-path=<odoo-addons>,<enterprise-addons>,<repo>/addons \
  -d <isolierte-development-db> -i gc_requirements \
  --test-enable --test-tags /gc_requirements --stop-after-init --without-demo=all
```

Danach mit `-u gc_requirements` und vorhandenen synthetischen Datensätzen wiederholen. Der Community-Vertrag ist kein Ersatz für diese Prüfung. Details und manuelle Abnahme: [RUNBOOK](docs/RUNBOOK.md).

## Bedienung und Freigaben

„Status ändern“ unterstützt alle acht Zustände, bei Zurückstellung/Ablehnung eine neue Begründung. „Umgesetzt“ bedeutet veröffentlicht oder produktiv verfügbar. Drei Sterne steuern nur die Anforderungspriorität. Follower und Aktivitäten sind intern; es entstehen keine automatischen Aktivitäten.

Ein bestätigter Merge archiviert das Original, kopiert fehlende Ticketquellen und vereinigt manuelle Kundenbeziehungen. Das Ziel behält seine eigene Redaktion/Klassifikation/Status. Originalanhänge, Chatter und Aktivitäten sind über „Erhaltene Originale“ erreichbar. „Archiviert“ findet alte Datensätze; Wiederherstellen entfernt keinen dauerhaften Mergeverweis. Endgültiges Löschen ist gesperrt.

Staging benötigt eine frische Kandidatenfreigabe, neutralisierte Daten und geprüfte Mail-/Integrationsisolation. Production benötigt eine separate Freigabe und einen benannten eingeschränkten Pilot. Der Development-Branch allein autorisiert keine Promotion. [Spezifikation](SPEC.md), [Technik](TECHNICAL_DESIGN.md), [Arbeitsregeln](AGENTS.md).
