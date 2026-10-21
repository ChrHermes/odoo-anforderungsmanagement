# Projektwissen

Stand: 21.10.2026. Verbindliche Fachentscheidungen stehen in `SPEC.md`, technische Regeln in `TECHNICAL_DESIGN.md`, Prüfgates in `IMPLEMENTATION.md` und Arbeitsregeln in `AGENTS.md`.

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
