# Codex-Auftrag: UI/UX-Feinschliff und Produktfarben für „Anforderungen“

## Kontext und Ziel

Die interne Odoo-App **„Anforderungen“** (`gc_requirements`) ist als lokal bedienbarer Odoo-18-UI-Demokandidat vorhanden; eine separate Odoo-20-Portierung existiert. Die vorliegenden Ansichten sind grundsätzlich gut. Ziel ist ein **gezielter, nativer Odoo-UI/UX-Feinschliff**, keine Neuentwicklung und keine Erweiterung um Dashboard, KI oder externe Frontends.

**Verbindliche Quellen:** `AGENTS.md`, `SPEC.md`, `TECHNICAL_DESIGN.md`, `IMPLEMENTATION.md`, `docs/STATUS.md`, `docs/DECISIONS.md`, `docs/PROJECT_MEMORY.md`, `docs/RUNBOOK.md` und – sofern vorhanden – `docs/COMPATIBILITY.md`, `docs/LOCAL_DEVELOPMENT.md` und `docs/ACCEPTANCE.md`. Lies diese und prüfe den tatsächlichen aktuellen Code sowie den Git-Status vor Änderungen. Halte technische IDs, vorhandene fachliche Logik und alle bereits vereinbarten Sicherheitsgrenzen stabil.

## 1. Verbindliche Produktfarben und neue Produkte

Die folgenden **exakten Hex-Farben** sind die initialen Standardwerte:

| Produkt | Standardfarbe |
|---|---|
| GridCal Operator | `#40d0d7` |
| GridCal Node | `#0068b1` |
| GridCal Core | `#4a0a7c` |
| GridCal Nexus **(neu)** | `#c51a82` |
| GridCal Allgemeines **(neu)** | `#fa4d0f` |

Anforderungen:

- Ergänze ein **pro Produkt konfigurierbares Farbfeld**, das die angegebenen exakten Hex-Werte speichern und bearbeiten kann. Verwende gegebenenfalls einen möglichst nativen Odoo-Farbwähler mit Hex-Unterstützung; ein minimaler, auf die App begrenzter Zusatz ist akzeptabel, wenn die Standard-Widgets dies nicht leisten.
- Lege **GridCal Nexus** und **GridCal Allgemeines** als neue, auswählbare Top-Level-Produkte an, **nur falls sie noch nicht existieren**. Sie müssen in der bestehenden Produktverwaltung und für Anforderungen nutzbar sein. Keine spekulativen Funktionsunterkategorien für die neuen Produkte anlegen.
- Setze die oben genannten Standardfarben bei Neuinstallation und für bestehende Produkte **nur dann, wenn noch keine individuell konfigurierte Farbe vorhanden ist**. Ein Modulupgrade darf Nutzerfarben, umbenannte Produkte, Kategorien und bestehende Anforderungen nicht überschreiben. Keine Duplikate erzeugen; bestehende technische/XML-IDs möglichst weiterverwenden. Seed-/`noupdate`-Semantik und Upgradeverhalten beachten.
- Produktfarben müssen ohne Codeänderung in **Anforderungen → Konfiguration → Produkte** änderbar sein, nur durch die bestehende Konfigurationsgruppe.
- Auf Kanban-Karten das Produkt mit seiner Farbe gut erkennbar darstellen, vorzugsweise **als kompakter farbiger Badge und/oder schmaler linker Farbakzent**. Keine großflächig bunt eingefärbten Karten. Beachte Lesbarkeit und Kontrast: Bei hellen Farben wie Operator-Türkis dunkle Schrift, bei dunklen Farben weiße Schrift. Auch bei fehlender Farbe ein sauberer neutraler Fallback.
- Eine Produktfarbe darf nicht als Ersatz für den Anforderungstyp oder die Prioritätssterne dienen.

## 2. Kanban-Status in logischer Reihenfolge

Die Kanban-Spalten sind **immer** in folgender Reihenfolge zu präsentieren:

1. Neu
2. In Prüfung
3. Bewertet
4. Geplant
5. In Umsetzung
6. Umgesetzt
7. Zurückgestellt
8. Abgelehnt

- Prüfe die tatsächliche Odoo-18-/Odoo-20-Implementierung der Statusgruppen (Selection, `group_expand`, Sortierung etc.) und setze die Reihenfolge **deterministisch** um, unabhängig von Datenbestand, zufälliger Erstellung oder Gruppierungsabfragen.
- **Zurückgestellt** und **Abgelehnt** sind rechts angeordnete Sonder-/Endbereiche, optisch leicht von der Hauptstrecke abgesetzt: z. B. subtile Trennung/Spacing und zurückhaltende Tönung der Spaltenüberschriften bzw. Spaltenfläche. „Zurückgestellt“ gern warm/neutral, „Abgelehnt“ dezent rosé/rot. Keine aggressiven Warnflächen und keine Veränderung der bestehenden Statussemantik oder Berechtigungen.
- Die Übersicht muss auch bei horizontalem Scrollen, leeren Gruppen und mehreren Einträgen konsistent bleiben. Das Kanban-Board bleibt die Landing-Ansicht, Liste bleibt verfügbar.

## 3. Kanban-Karten: bessere Informationshierarchie und Typfarben

Aktuell wirken Produkt und Funktionsbereich in den Karten gleich groß/gleich wichtig. Bitte ändern:

- **REQ-Nummer und Titel** bleiben gut erkennbar.
- **Produkt** optisch stärker, mit seiner konfigurierten Produktfarbe.
- **Funktionsbereich** darunter klar sekundär darstellen: kleinere, dezente Typografie, gegebenenfalls gekürzter relativer Pfad statt vollständiger Wiederholung des bereits separat angezeigten Produkts (z. B. `ANALYTIC / Events / Mailing` statt `GridCal Node / ANALYTIC / Events / Mailing`). Der vollständige Pfad muss bei Bedarf erreichbar bleiben, z. B. per Tooltip oder in der Detailansicht.
- **Anforderungstyp** als dezentes farbiges Tag/Badge unterscheiden: Funktionswunsch, Verbesserung, Fehler/Bug. Farben sollen sich harmonisch in Odoo einfügen, deutlich unterscheidbar und lesbar sein; keine Änderung an internen Selection-Werten.
- **Drei-Sterne-Priorität**, verantwortliche Person, Kunden-/Ticketanzahlen und offene Aktivitäten beibehalten. Karten übersichtlich und nicht zu hoch machen; keine Fachinformationen entfernen.
- Gute Darstellung bei fehlendem Funktionsbereich, ohne Kunden/Tickets sowie in engen Kanban-Spalten sicherstellen.

## 4. Ursprüngliche Ticketbeschreibung in der Anforderung sichtbar machen

Die fachliche Anforderungsbeschreibung und die als unveränderliche Momentaufnahme gespeicherte **ursprüngliche Ticketbeschreibung** sind strikt unterschiedliche Inhalte.

- Prüfe zunächst, ob die bisher fehlende Sichtbarkeit lediglich daran liegt, dass die lokale UI-Demo für den betrachteten Datensatz **0 verknüpfte Tickets** enthält. **Keinen Bug behaupten, bevor Ursache/Benutzerrechte geprüft wurden.**
- Im Reiter **„Kunden & Tickets“** müssen **pro berechtigt lesbarem verknüpftem Ticket** Ticketnummer, Titel, Kunde und die **beim Verknüpfen gespeicherte Originalbeschreibung** eindeutig zugeordnet und gut auffindbar sein. Das darf durch eine schmale, native Anzeige/einen autorisierten Viewer, einen Aufklappbereich oder einen eindeutigen Button pro Ticket erfolgen; bevorzuge sichere bestehende Mechanismen vor einem aufwendigen Custom-Frontend.
- Der vollständige Ticketverlauf bleibt ausschließlich im Helpdesk; ein Link zur aktuellen Ticketansicht ist sinnvoll. Spätere Änderungen des Tickets ändern die gespeicherte Momentaufnahme nicht.
- **Datenschutz ist ein hartes Abnahmekriterium:** Bestehende Helpdesk-ACLs/Record Rules/Feldrechte sind für jedes Ticket bei jedem Lesezugriff serverseitig zu prüfen. Momentaufnahmen nicht in allgemein lesbare Requirement-Felder, Chatter, Suchindizes, öffentliche Relationsfelder oder ungeprüfte API-/Exportantworten kopieren. Benutzer ohne Ticket-Leserecht dürfen weder die Beschreibung noch deren Inhalte über Listen, Export, `read`, `search_read`, `read_group` oder sonstige indirekte Pfade auslesen. Bestehende Sicherheitsarchitektur nicht abschwächen.
- Für die **lokale synthetische UI-Demo** mindestens eine Anforderung mit einem Beispiel-Helpdesk-Ticket **und nichtleerer, sichtbar autorisierter Original-Momentaufnahme** bereitstellen. Zusätzlich mit einem unberechtigten internen Demo-Benutzer den negativen Anzeigefall ermöglichen/testen. Demo-/Testdaten dürfen nicht in bestehende reale Datensätze oder Odoo.sh/Staging/Production gelangen.
- Wenn keine Ticketquelle vorliegt, soll statt einer leeren, missverständlichen Oberfläche ein deutlicher Hinweis wie „Keine Helpdesk-Tickets verknüpft“ erscheinen.

## 5. Versionen, Tests und Qualitätssicherung

- **Odoo 18** ist die primäre Version für lokalen UI-Test und visuelle Abnahme. Die gleichen Änderungen müssen auch in der separaten **Odoo-20-Portierung** umgesetzt werden, ohne ihre bisherige Kompatibilität zu verschlechtern.
- Prüfe vor dem Arbeiten die beiden Branches `codex/initial-mvp` (18) und `codex/20.0-port` (20) und die dokumentierte Strategie in `docs/COMPATIBILITY.md`. Ändere nur klar zugeordnete Development-Branches; keine ungeprüften Merges oder Force-Pushes. Anwenderänderungen und uncommittete Arbeit unangetastet lassen.
- Ergänze Tests für: deterministische Statusreihenfolge; vorhandene/neue Produktfarben; neue Produkte ohne Seed-Duplikate; manuelle Farbänderung bleibt bei Upgrade erhalten; Kanban- und Formular-Views; geschützte Ticket-Momentaufnahmen inklusive positiver/negativer Rechtefälle; synthetische Demo-Verknüpfung.
- Bestehende Tests und Install-/Upgrade-Prüfungen für **beide Odoo-Versionen** weiterhin ausführen. Unterschied zwischen Community-Vertrag und echter Enterprise-Abnahme ausdrücklich dokumentieren.
- Falls Browserautomatisierung zur Verfügung steht: die lokale UI tatsächlich öffnen und **Screenshots des Kanban-Boards, der Produktkonfiguration und einer autorisierten Ticket-Momentaufnahme** anfertigen bzw. deren Pfade dokumentieren. Ein bloßes erfolgreiches XML-Laden ist keine visuelle Abnahme. Falls Browserautomatisierung fehlt, konkret dokumentieren und eine kurze manuelle Prüfanleitung liefern.
- Vermeide unnötiges JavaScript/CSS; ergänzende Styles nur auf diese App beschränken und auf schmalen Fenstergrößen sowie die Standard-Odoo-Ansichten achten. Keine Auswirkungen auf das bestehende Helpdesk-Design.

## 6. Autonomie, Dokumentation und Git

- Arbeite die Aufgabe **möglichst autonom bis zu einem funktionsfähigen, getesteten UI-Ergebnis** ab, nicht nur bis zum ersten Commit. Analysiere Fehler und korrigiere sie selbstständig, soweit sicher möglich.
- Dokumentiere Entscheidungen und tatsächliche Testnachweise in `docs/DECISIONS.md`, `docs/STATUS.md`, `docs/PROJECT_MEMORY.md`, `docs/ACCEPTANCE.md` und der lokalen Entwicklungsanleitung, soweit betroffen. Halte die Projektunterlagen konsistent. Keine unnötige Änderung bereits verabschiedeter Fachentscheidungen.
- Committe eigenständig in sinnvollen Einheiten und pushe die **jeweiligen Development-Branches** nach Möglichkeit. Bei fehlendem Remote-Zugriff lokal weiterarbeiten und den Status dokumentieren. Keine Änderung an Staging oder Production, keine Migration echter Daten, keine Secrets oder Enterprise-Quelltexte committen.
- Abschlussbericht: je Version geänderter Commit, Teststatus (inkl. tatsächlich ausgeführter Befehle), aktuelle Screenshots/Prüfpfade, verbleibende Risiken, und offene Enterprise-Abnahmen.

## Abnahmekriterien (Checkliste)

- [ ] Kanban zeigt alle acht Status in der vorgegebenen Reihenfolge; Zurückgestellt/Abgelehnt sind dezent rechts abgesetzt.
- [ ] Alle fünf Produkte einschließlich Nexus und Allgemeines sind vorhanden, mit den **exakten** angegebenen Standardfarben.
- [ ] Produktfarben sind in der Odoo-Konfiguration änderbar und bleiben bei Modulupgrades erhalten.
- [ ] Kanban-Karten zeigen Produkte farblich hervorgehoben, Funktionsbereiche visuell untergeordnet und Typen als unterscheidbare Tags.
- [ ] Prioritätssterne, Tickets/Kunden-Zähler, Verantwortliche und Aktivitäten funktionieren weiterhin.
- [ ] Eine Demo-Anforderung zeigt die ursprüngliche Beschreibung eines zugeordneten synthetischen Tickets an; bei fehlendem Ticket gibt es eine verständliche Leeranzeige.
- [ ] Unberechtigte Benutzer können die Originalbeschreibung nicht lesen, auch nicht über ORM/API/Export; bestehende Tests bleiben erfolgreich.
- [ ] Installation, Upgrade und App-Tests in Odoo 18 und Odoo 20 erfolgreich, soweit verfügbar; fehlende Enterprise-Abnahmen klar ausgewiesen.
- [ ] Git-Commits, Dokumentation, Screenshots bzw. manuelle UI-Prüfanleitung und Abschlussbericht liegen vor.

**Beginne mit einer Bestandsaufnahme und setze die Änderungen anschließend eigenständig um. Frage nur bei einem wirklich entscheidungspflichtigen fachlichen Konflikt nach.**
