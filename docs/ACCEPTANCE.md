# Abnahmenachweise

## UX- und Produktfarben-Kandidat, 22.10.2026

Versionen 18.0.1.2.0 und 20.0.1.2.0. Native Hex-Farbkonfiguration mit fünf exakten Standardwerten, Nexus/Allgemeines ohne erfundene Kategorien, additive Defaults, vollständige Statusreihenfolge/Leergruppen und kompakte Kartenhierarchie umgesetzt. Farbe bleibt unabhängig von Typ/Priorität; Config-ACL und serverseitige Farbvalidierung geprüft. Ursprüngliche Tickettexte bleiben strikt im privaten Autorisierungspfad, Formular enthält keine neue allgemein lesbare Snapshotkopie.

Geprüfte Kandidaten: 18 `bc2cc78`, 20 `c15a70e`. Finale normale Verträge und beide 18er Browserchecks nochmals erfolgreich; Push beider Linien mangels HTTPS-Anmeldung fehlgeschlagen. Somit lokale Nachweise, kein gehosteter Development-/Enterprise-Build.

| Lauf | 18 | 20 |
|---|---|---|
| Frisch / vorheriger Kandidat / echtes Upgrade | 32 / 27 / 32 Tests | 34 / 29 / 32 Tests (frisch 32 App + 2 Core-Webfälle) |
| Zusätzlicher aktueller Install-/Upgrade-Vertrag | 32 / 32 | 34 / 32 |
| Individuelle Farbe über Upgrade | #123456 erhalten | #123456 erhalten |
| Nexus bereits manuell vorhanden | Dieselbe ID übernommen, kein Duplikat | Dieselbe ID übernommen, kein Duplikat |
| Daten-/Rechteinventur, negative Proben | Bestanden | Bestanden |
| Reale Browser-UX-/Rechteprüfung | Lokale synthetische UI-Demo bestanden | Nicht ausgeführt |

Playwright prüft alle acht Gruppen auch ohne Suchtreffer, Standardfarben/Schriftkontrast, Hex-Eingabe und Wiederherstellung der Ausgangsfarbe, schmale Ansicht, Typ-/Produktbadges, relative Kategoriepfade, autorisierten Originalviewer und klare Ticket-Leeranzeige. Ein zweiter interner App-Benutzer ohne Helpdesk-/Config-Rechte erhält keine Momentaufnahme im Viewer/Adapter/read/search/group/export/count. Keine JavaScriptfehler/externen Browserrequests. Screenshots in `.local/dev/browser-ux/` visuell geprüft: `kanban.png`, `kanban-terminal.png`, `kanban-narrow.png`, `product-configuration.png`, `authorized-snapshot.png`, `denied-snapshot.png`, `no-tickets.png`.

Die bestehende Suite einschließlich genauer synthetischer Ticket-Record-Rules, Rechteentzug und alternativer generischer Schnittstellen bleibt erhalten. **Community-Vertrag und lokale synthetische UI sind keine Enterprise-Abnahme.** Tatsächliche Enterprise-/Custom-Regeln, Mailautomationen, Odoo-20-Browser, fremde Hostplattformen und vollständiger Major-Upgrade bleiben offen. Keine Staging-/Production-Aktion oder Freigabe.

## Ergänzung: lokale UI-Demo, 22.10.2026

Die lokale persistente Odoo-18-Weboberfläche unter localhost:8069 ist tatsächlich erreichbar und mit benanntem internem Entwicklungsbenutzer bedienbar. Playwright/Chromium prüft Anmeldung, eigene lokale App-Kachel, native Kanban-/Listenansichten, Erstellen/Bearbeiten mit eigener Redaktion und Produkt-/Kategoriezuordnung, drei Sterne, Statuswizard, Chatternotiz, manuelle Aktivität sowie Ticketverknüpfung/Quellenviewer im **synthetischen Helpdesk**. Alle sieben Browserprüfschritte bestanden, keine JS-Fehler oder externen Browserrequests; Screenshots von Launcher, Kanban, Detail und Quelle visuell geprüft. Wiederholung nach lokalem Reset ebenfalls erfolgreich.

Moduleupgrade und Stop/Start erhalten die interaktiv angelegten Daten einschließlich Aktivität, Notiz und Momentaufnahme. Bestehender Contract-Testtreiber weiterhin separat: 27/27 nach Install, 27/27 nach Upgrade und erfolgreiche Erhaltungsinventur. Anleitung und Nachweise: [LOCAL_DEVELOPMENT](LOCAL_DEVELOPMENT.md), [RUNBOOK](RUNBOOK.md). Dies schließt die zuvor fehlende lokale Browserprüfung für den synthetischen Modus; **Enterprise-/Custom-Helpdesk-, macOS-/Apple-Silicon- und separater Windows-Browsernachweis bleiben offen**. Keine Odoo.sh-/Staging-/Production-Freigabe.

## Historische Nachweise

Stand: 21.10.2026. **Vertrag** bedeutet echte Odoo-18-ORM/Views/Mail-Laufzeit mit ausdrücklich synthetischem Helpdesk-Modell, nicht Odoo Enterprise. Ein bestandener Vertrag ist kein bestandenes Enterprise-/Staging-Gate. SPEC-Checkliste bleibt bis zur fachlichen Abnahme unverändert.

| SPEC §11 | Implementierung / automatisierter Nachweis | Enterprise-/UI-Abnahme |
|---|---|---|
| Eigene App, kein Portalmenü | Manifest, Menüs, SVG-Icon; Views geladen | Launcher visuell prüfen |
| Explizite Pilotgruppe | ACLs, interne globale Regeln; Portal/Fremdbenutzer und versehentlich berechtigter Portalbenutzer verweigert | Benannte Pilotrollen prüfen |
| Pflichtdaten, unveränderliche Nummer | `test_requirements`: Inhalt/Pflichtwerte, Sequenz, direkte Manipulation | Frische Enterprise-Installation |
| Hierarchie, Seeds, Config-ACL | Getrennte BASE-Äste, Zyklen/Produktwechsel/Archivierung/Selektierbarkeit; echter Vertragsupgrade mit geänderten Seeds | Bestehende Klassifikationen prüfen |
| Kanban/List/Form/Suche/Chatter | `get_view` und XML-Installation, Filter, Tracking und Aktivitäten | Interaktive Ansichten/Favoriten prüfen |
| Priorität 0..3, unabhängig | Default/Werte validiert, Ticketpriorität bei Notizen unverändert | Sterne visuell prüfen |
| Ticketwizard und n:m | `test_helpdesk`: neue/bestehende Anforderung, idempotentes Verknüpfen, native Action-Bindings, Navigation | Aktionen im echten Helpdesk prüfen |
| Eigene Redaktion, immutable Quellen | Capture vor Ticketänderung, Snapshot-Schreibverweigerung, keine automatische redaktionelle Übernahme | Angepasste Ticketbeschreibung prüfen |
| Eindeutige Organisationen | Mehrere Kontakte/Tickets derselben Firma, manuelle Beziehungen, live Partneränderung | Reale Partnerstruktur validieren |
| Exakte Ticketvertraulichkeit | `test_security`: ACLs, eigene globale Ticketregel, direkte Read/Search/Group/Export/Count-Wege, kein Relationsorakel, Parentregel, Rechteentzug im Viewer | **Zwingend: zwei reale Benutzer mit/ohne genaues Ticketrecht, alle Custom-/Company-Regeln** |
| Statusregeln und Gründe | Alle acht Zustände, neue Begründung je Übergang, direkte ORM-Versuche, Historie und Wizard | Fachliche Übergänge prüfen |
| Nur interne Ticketnotizen | Drei Status × zwei Tickets = sechs Notizen, Wiederholung ohne Übergang = keine Zusatznotiz; keine Mail/Notification, Ticket unverändert | **Zwingend: echte Automationen/SMTP in neutralisierter Umgebung** |
| Interne Follower/manuelle Aktivitäten | Creator/Assignee, direkter Follower-ORM-Schutz, externe Empfänger/Aktivitätszuweisung verweigert, keine Autoaktivitäten | Mentions/Activity-Übersicht prüfen |
| Vorschläge/erhaltender Merge | Bounded Produkt-/Titelsuche, Bestätigung, Zugriffsprüfung, Überlappung, Provenienz, Chatter/Aktivitäten/Anhang, Redirectketten | Mergeflow und Originalnavigation prüfen |
| Archivieren/Restore, kein Delete | ORM-/UI-Löschschutz, Archivsuche/Restore, Aktivitätserhalt | Rollen und Restore prüfen |
| Veröffentlicht mit Datum | Pflichtdatum wird gesetzt; Rückwärtsübergang erhält letztes Datum; Releasefelder getrennt | Veröffentlichungssemantik bestätigen |
| Kein zusätzlicher MVP-Umfang | Kein Dashboard/AI/externes Frontend/Releaseplaner hinzugefügt | Keine weitere Funktion nötig |

## Ausgeführter reproduzierbarer Durchlauf

`python3 scripts/test_contract.py`: frische Installation und 26 Tests fehlerfrei; tatsächliches Modulupgrade und dieselben 26 Tests fehlerfrei. Geänderte Produktnamen/Reihenfolge, umbenannter archivierter Funktionsbereich, existierende REQ-Referenz, unveränderliche Quelle und physischer Filestore-Anhang nach Upgrade erhalten. Native Odoo-`Form`-Erfassung, Wizarddefaults, alle vier Wizard-Views, Gruppierung und Referenzsuche zusätzlich geprüft. Aggregatlesen für 1.000 Anforderungen/2.000 unterschiedlichen Tickets und Quellen benötigt 13 SQL-Abfragen bei kaltem Cache. Kein Last-/Parallelbenutzerbenchmark. Teststacks danach entfernt.

Nicht ausgeführt: Odoo-Enterprise-Installation, echte Helpdesk-Custom-Views/-Automationen, Odoo.sh-Build, Staging, Production und visuelle Browserabnahme. Browserwerkzeug konnte die Laufzeit nicht initialisieren (`Importing module "node:process" is not allowed in node_repl`). XML-/Modellprüfungen ersetzen diesen visuellen Nachweis nicht.

Extern reproduziert: GitHub-Läufe [39678680433](https://github.com/ChrHermes/odoo-anforderungsmanagement/actions/runs/39678680433) (`9ef47ad`) und [39679093289](https://github.com/ChrHermes/odoo-anforderungsmanagement/actions/runs/39679093289) (`e300220`) erfolgreich. App-Code seit `9ef47ad` identisch; `e300220` fixiert nur CI-Versionen und dokumentiert Nachweise. Beide Läufe sind ausdrücklich synthetische Community-Verträge.

## Gezielte Sicherheitsgrenzen

- Private Quellen haben keine normale ACL und keine öffentliche Parent-Relation. Ein Superuser mit bewusst administrativem Zugriff bleibt wie in Odoo üblich vertrauenswürdig; App-/Config-Benutzer erhalten diesen Zugriff nicht.
- Sichtbare Ticket-/Kundenanzahlen dürfen auch geschützte Quellen aggregieren. Detailaktionen geben nur autorisierte Ticketkunden aus; manuelle Kunden sind unabhängige redaktionelle App-Daten.
- Custom-Helpdesk-Read-/Feldbeschränkungen werden im Adapter zusätzlich über `read` berücksichtigt. Externe benutzerdefinierte Automationen auf `mail.message.create` müssen vor Freigabe kontrolliert werden.
- Normales Verknüpfen ist bei vorhandener Quelle idempotent. Parallel konkurrierende Verknüpfungen werden zusätzlich durch SQL-Eindeutigkeit abgesichert; ein Konflikt darf die gesamte RPC-Transaktion zurückrollen.
- Merge-Zeilensperren schützen die beiden Anforderungen. Ein eigener paralleler Mehrprozess-/Deadlocktest und reales Lastprofil stehen noch aus.

## Naming-Kandidat 18.0.1.1.0, 22.10.2026

`python3 scripts/test_contract.py --baseline-ref 36085f50b66102a85515fd004abae59120848af1`: Neuinstallation 27 Tests, Installation des alten Kandidaten 26 Tests, Upgrade auf neuen Stand 27 Tests; alle ohne Fehler. Locale-Test lädt `i18n/de.po` und prüft App-/Launcher-/Aktions-/Gruppennamen, Status/Typ/Priorität sowie geerbte deutsche Aktivitäts-/Metadatenlabels. Die gesamte bisherige Suite bleibt erhalten.

Erweiterte Inventur erhält Klassifikation, Referenz/Sequenz, private Snapshots und überlappende Capture-/Mergeprovenienz, Ticket-/Kundenzuordnung, archivierte Originale, Chatter samt Tracking, Aktivitäten/Follower, physischen Anhang sowie XML-IDs, Gruppen und aktuelle Zugriffsgrenzen. Absichtliche Titel-/Anhangveränderungen werden erkannt und zurückgerollt. Statische Syntax-/Paket-/XML-/ACL-Prüfung, Ruff und Formatierung bestanden. **Kein Enterprise- oder 18->20-Migrationsnachweis**; gesonderte Matrix in [COMPATIBILITY](COMPATIBILITY.md).

## Odoo-20-Port, 22.10.2026

Separater Development-Branch `codex/20.0-port`, Version `20.0.1.1.0`. Echte Odoo-20.0-20261015-Community-Laufzeit mit synthetischem Helpdesk: Neuinstallation 27 App-Tests plus 2 Webtests erfolgreich; Modulupgrade 27 App-Tests erfolgreich. Dieselbe Daten-/Rechteinventur einschließlich strukturiertem Tracking und physischem Filestore sowie negative Korruptionsproben erfolgreich. Gesamtumfang der bisherigen App-Tests bleibt erhalten. Native APIs und zusätzliche `mail_tracking`-Abhängigkeit dokumentiert. **Kein Enterprise-Kompatibilitäts- oder echter 18->20-Migrationsnachweis**.
