# Codex-Auftrag: Release- und Meilensteinplanung für „Anforderungen“

## Ziel

Erweitere die bestehende interne Odoo-App `gc_requirements` („Anforderungen“) um eine zentrale **Release- und Meilensteinplanung**.

Die Erweiterung soll es Kundendienst, Entwicklung, Product Ownern und weiteren Stakeholdern ermöglichen, Anforderungen einem geplanten Release oder Meilenstein zuzuordnen und den Fortschritt der Planung übersichtlich nachzuvollziehen.

Die App bleibt ein internes Anforderungsmanagement. Es soll kein vollständiges Projektmanagement, keine Sprintverwaltung und keine öffentliche Roadmap entstehen.

Implementiere die Erweiterung für **Odoo 18 und Odoo 20** unter Beibehaltung der bestehenden Versionsbranches.

## 1. Projektkontext und Arbeitsweise

Lies vor der Entwicklung:

- `AGENTS.md`
- `SPEC.md`
- `TECHNICAL_DESIGN.md`
- `IMPLEMENTATION.md`
- `docs/STATUS.md`
- `docs/DECISIONS.md`
- `docs/PROJECT_MEMORY.md`
- `docs/COMPATIBILITY.md`, sofern vorhanden

Untersuche die bestehende Modulstruktur und verwende vorhandene Architekturkonventionen.

Arbeite möglichst eigenständig, teste nach jedem größeren Implementierungsschritt und dokumentiere relevante Entscheidungen.

Verändere vorhandene fachliche Funktionen, technische IDs und Datenmodelle nur, wenn dies notwendig und mit einem sicheren Upgrade vereinbar ist.

## 2. Gemeinsames Planungsmodell

Implementiere ein eigenständiges Odoo-Modell, vorzugsweise `gc.requirement.milestone`.

Ein Datensatz repräsentiert entweder:

- ein **Release**, beispielsweise „GridCal Node 2027.1“
- einen **Meilenstein**, beispielsweise „SCADA-Ausbau Q2 2027“

Beide Typen teilen sich die grundlegende Verwaltung.

### Felder

Vorgesehen sind:

- Eindeutige interne Referenz, beispielsweise `MS-0001`
- Bezeichnung
- Typ: Release oder Meilenstein
- Produktzuordnung
- Optionale Versionsbezeichnung bei Releases
- Beschreibung (Rich Text)
- Optionales geplantes Datum bzw. Planungszeitraum
- Optionales tatsächliches Abschlussdatum
- Status: Entwurf, Geplant, Aktiv, Abgeschlossen/Veröffentlicht, Abgesagt
- Verantwortliche Person
- Zugeordnete Anforderungen
- Aktiv-/Archivierungskennzeichen

Ein Release benötigt eine Produktzuordnung. Meilensteine dürfen produktübergreifend sein.

Der sichtbare Abschlussstatus soll abhängig vom Typ als „Veröffentlicht“ beziehungsweise „Abgeschlossen“ bezeichnet werden, sofern dies mit vertretbarem Aufwand nativ umsetzbar ist.

Verwende Odoos bestehende Mechanismen für Chatter, Änderungsverfolgung und Aktivitäten.

## 3. Zuordnung von Anforderungen

Ergänze am bestehenden Anforderungsmodell ein optionales relationales Feld `milestone_id`.

Für den MVP gilt:

- Eine Anforderung kann maximal einem Release oder Meilenstein zugeordnet sein.
- Die Zuordnung kann jederzeit geändert oder entfernt werden.
- Änderungen müssen im Chatter nachvollziehbar sein.
- Für produktbezogene Releases ist nur die Zuordnung von Anforderungen desselben Produkts zulässig.
- Produktübergreifende Meilensteine dürfen Anforderungen unterschiedlicher Produkte enthalten.
- Die Prüfungen müssen serverseitig erfolgen.
- Bereits bestehende Anforderungen bleiben beim Modulupgrade unverändert und zunächst ohne Planungszuordnung.

Achte darauf, dass auch eine nachträgliche Änderung der Produktzuordnung einer Anforderung keine unbemerkte ungültige Release-Zuordnung erzeugt.

## 4. Erweiterung der Anforderungsdetailansicht

Erweitere den Reiter „Weitere Informationen“ um den Bereich **Planung**.

Zeige:

- Zielrelease / Meilenstein als auswählbares Many2One-Feld
- Geplanten Termin bzw. Zeitraum als Information aus dem Planungseintrag
- Optionalen direkten Link zum Planungseintrag

Trenne diesen Bereich visuell von den bereits vorhandenen Feldern zur tatsächlichen Umsetzung.

Die bestehenden Felder bleiben erhalten:

- Betroffene Version
- Veröffentlichte Version
- Veröffentlicht am
- Umsetzungshinweis
- Entwicklungsreferenz

Wichtig: Zielrelease und tatsächlich veröffentlichte Version sind fachlich unterschiedliche Informationen.

Keine automatische Übernahme oder Überschreibung bestehender Veröffentlichungsdaten.

## 5. Zentrale Releaseplanung

Erstelle einen neuen Menüpunkt:

**Anforderungen → Releaseplanung**

Die Oberfläche soll eine übersichtliche interne Planung ermöglichen.

### Gewünschte Funktionen

- Übersicht aller Releases und Meilensteine
- Unterscheidung nach Typ
- Anzeige des zugehörigen Produkts inklusive vorhandener Produktfarbe
- Geplanter Termin bzw. Zeitraum
- Status des Planungseintrags
- Anzahl zugeordneter Anforderungen
- Anzahl der Anforderungen nach Bearbeitungsstatus
- Direkte Navigation zu den enthaltenen Anforderungen
- Filter nach Produkt, Typ, Status und geplantem Zeitraum
- Darstellung von Anforderungen ohne Planungszuordnung

Bevorzuge eine native Odoo-Implementierung mit Listen-, Kanban- und Formularansichten.

Eine kompakte, informative Übersicht mit Statusverteilung oder Fortschrittsanzeige ist erwünscht.

Vermeide eine aufwendige eigene OWL-Anwendung, sofern die Anforderungen mit nativen Odoo-Komponenten sinnvoll umgesetzt werden können.

## 6. Detailansicht eines Releases oder Meilensteins

Beim Öffnen eines Planungseintrags sollen sichtbar sein:

- Stammdaten und Planungstermin
- Beschreibung
- Verantwortliche Person
- Enthaltene Anforderungen
- Deren Status, Typ, Priorität und Produkt
- Chatter und Aktivitäten

Die Anforderungen sollen anklickbar sein und zu ihrer bestehenden Detailansicht führen.

Ermögliche eine einfache Zuordnung bestehender Anforderungen, idealerweise durch eine native Odoo-Auswahlliste.

## 7. Status und Abschlusslogik

Der Status eines Releases oder Meilensteins ist unabhängig vom Status der enthaltenen Anforderungen.

Insbesondere:

- Das Zuordnen zu einem Release setzt eine Anforderung nicht automatisch auf „Geplant“.
- Das Veröffentlichen eines Releases setzt Anforderungen nicht automatisch auf „Umgesetzt“.
- Bei offenen Anforderungen in einem abzuschließenden Planungseintrag erscheint eine Warnung mit ausdrücklicher Bestätigungsmöglichkeit.
- Abgelehnte, zurückgestellte und archivierte Anforderungen müssen in Zählern und Übersichten fachlich nachvollziehbar behandelt werden.
- Der Abschluss eines Planungseintrags darf bestehende Veröffentlichungsangaben von Anforderungen nicht verändern.

Änderungen und Abschlussentscheidungen sollen nachvollziehbar dokumentiert werden.

## 8. Berechtigungen und Datenschutz

Die Releaseplanung ist ausschließlich für berechtigte interne Benutzer der App sichtbar.

Für den MVP dürfen Mitglieder der bestehenden App-Pilotgruppe Planungseinträge erstellen und bearbeiten.

Beachte:

- Keine Portal- oder Kundenberechtigungen
- Keine unbeabsichtigten Kundenbenachrichtigungen
- Keine Offenlegung geschützter Helpdesk-Ticketinformationen über Planungseinträge
- Bestehende ACLs, Record Rules und Snapshotschutz unverändert erhalten
- Keine Verwendung von `sudo()` für allgemein lesbare Planungsergebnisse, wenn dadurch fremde Daten sichtbar werden könnten

## 9. Produktfarben und Gestaltung

Verwende die bereits vorhandenen konfigurierbaren Produktfarben.

Die Standardfarben lauten:

- GridCal Operator: `#40d0d7`
- GridCal Node: `#0068b1`
- GridCal Core: `#4a0a7c`
- GridCal Nexus: `#c51a82`
- GridCal Allgemeines: `#fa4d0f`

Ändere individuelle Farbeinstellungen bei Modulupgrades nicht.

Die Releaseplanung soll sich optisch nahtlos in das bereits überarbeitete Kanban-Design einfügen.

## 10. Testdaten und Qualitätssicherung

Erweitere die synthetische lokale Demo um mehrere Releases und Meilensteine.

Erzeuge Beispiele mit:

- Unterschiedlichen Produkten und Produktfarben
- Produktübergreifenden Meilensteinen
- Unterschiedlichen Planungsstatus
- Anforderungen ohne Planungszuordnung
- Geplanten und umgesetzten Anforderungen innerhalb desselben Releases
- Bereits veröffentlichten Releases mit noch offenen Anforderungen

Implementiere automatisierte Tests für:

1. Erstellung und Änderung von Releases und Meilensteinen
2. Produktzuordnung und produktspezifische Einschränkungen
3. Zuordnung, Wechsel und Entfernung eines Zielmeilensteins
4. Unveränderte Anforderungsstatus bei Planungsänderungen
5. Abschlusswarnungen und fehlende automatische Fertigstellung
6. Zugriffsrechte und Datenschutz
7. Filter, Ansichten und Zähler
8. Datenbestandserhalt beim Modulupgrade
9. Kompatibilität mit Odoo 18 und Odoo 20

Führe die vorhandenen Installations-, Upgrade- und Regressionstests weiterhin aus.

Führe außerdem einen Browser-Smoke-Test der lokalen Odoo-18-Umgebung durch, sofern diese verfügbar ist.

Eine synthetische Helpdesk-Umgebung ist keine Enterprise-Abnahme. Kennzeichne die entsprechenden Einschränkungen.

## 11. Entwicklung für Odoo 18 und 20

Die bestehende Branchstruktur bleibt erhalten:

- `codex/initial-mvp` – Odoo 18
- `codex/20.0-port` – Odoo 20

Implementiere die Erweiterung zuerst auf Odoo 18 und übertrage sie danach kontrolliert auf Odoo 20.

Beachte versionsspezifische Unterschiede in ORM, Views und Sicherheitsmechanismen.

Erstelle nachvollziehbare Commits. Ein Push in die jeweils autorisierten Development-Branches ist erlaubt, sofern der Git-Zugang funktioniert.

Keine Force-Pushes und keine Änderungen auf Staging oder Production ohne ausdrückliche Freigabe.

## 12. Dokumentation

Aktualisiere:

- `SPEC.md`
- `TECHNICAL_DESIGN.md`
- `IMPLEMENTATION.md`
- `docs/STATUS.md`
- `docs/DECISIONS.md`
- `docs/PROJECT_MEMORY.md`
- `docs/RUNBOOK.md`
- `docs/COMPATIBILITY.md`, sofern vorhanden

Dokumentiere die neue Architektur, Änderungen am Datenmodell, Testresultate und Besonderheiten für Odoo 18 und 20.

## 13. Abschlusskriterien

Der Auftrag gilt im verfügbaren lokalen Entwicklungsumfang als abgeschlossen, wenn:

- Releases und Meilensteine erstellt und gepflegt werden können.
- Anforderungen einem Zielrelease oder Meilenstein zugeordnet werden können.
- Die Planung in einer eigenen internen Übersicht sichtbar ist.
- Die enthaltenen Anforderungen samt Status nachvollziehbar dargestellt werden.
- Änderungen an der Planung keine Anforderungsstatus oder tatsächlichen Veröffentlichungsdaten unbeabsichtigt verändern.
- Die vorhandene App weiterhin funktioniert.
- Automatisierte Tests und vorhandene Regressionstests erfolgreich sind.
- Die erforderlichen Tests für beide Odoo-Versionen durchgeführt wurden.
- Änderungen committed und möglichst gepusht sind.
- Noch offene Enterprise- und Migrationstests ausdrücklich dokumentiert wurden.

Arbeite nach Möglichkeit selbstständig bis zu diesem Ergebnis. Stoppe nicht nach dem Erstellen des Datenmodells, sondern implementiere auch die Benutzeroberfläche, die Testabdeckung und die Dokumentation.

Vermeide unnötige Rückfragen bei nicht kritischen technischen Entscheidungen. Halte wesentliche Annahmen im Projektgedächtnis fest.

---

### Ergänzung: GitLab-Worktimes-Verknüpfung

Ergänze im Reiter **„Weitere Informationen“** der Anforderungsdetailansicht neben der bestehenden **Entwicklungsreferenz** ein zusätzliches, optionales Feld **„Worktimes (GitLab)“**.

**Anforderungen:**
- Eigenständiges URL-Feld zur Verknüpfung mit dem zugehörigen Worktimes-Eintrag in GitLab.
- Komfortable Eingabe und Bearbeitung über das Odoo-Formular.
- Bei hinterlegter URL soll ein anklickbarer Link bzw. eine Schaltfläche **„In GitLab öffnen“** erscheinen, die das Ziel in einem neuen Browser-Tab öffnet.
- Das Feld bleibt unabhängig von der bestehenden Entwicklungsreferenz.
- Keine GitLab-API-Integration oder automatische Synchronisierung erforderlich.
- Bestehende Datensätze bleiben beim Modulupgrade unverändert; das neue Feld ist standardmäßig leer.
- Umsetzung und Tests für Odoo 18 und Odoo 20.

Verwende nach Möglichkeit native Odoo-Widgets und verzichte auf eigene JavaScript-Komponenten.
