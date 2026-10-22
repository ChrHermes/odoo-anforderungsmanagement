# Korrektur: Manuelle Statusverwaltung der Releaseplanung

In der neuen Release- und Meilensteinplanung der Odoo-App „Anforderungen“ muss die Statusverwaltung korrigiert bzw. ergänzt werden.

## Problem

Aktuell lassen sich Releases und Meilensteine offenbar nicht unabhängig von ihren zugeordneten Anforderungen zwischen den Bearbeitungsstatus verschieben.

Es entsteht der Eindruck, dass der Status aus dem Bearbeitungsstand der Anforderungen abgeleitet wird. Außerdem fehlt eine komfortable Möglichkeit, einen neu erstellten Entwurf manuell auf „Geplant“ oder „Aktiv“ zu setzen.

Dies entspricht nicht dem vorgesehenen fachlichen Verhalten.

## 1. Status ausschließlich manuell verwalten

Der Status eines Releases oder Meilensteins muss ein eigenständig gespeichertes und bearbeitbares Feld sein.

Vorgesehene Status:

1. Entwurf
2. Geplant
3. Aktiv
4. Abgeschlossen / Veröffentlicht
5. Abgesagt

Der Status darf niemals automatisch anhand der zugeordneten Anforderungen verändert werden.

Insbesondere dürfen folgende Vorgänge keinen automatischen Statuswechsel auslösen:

- Eine Anforderung wird zugeordnet oder entfernt.
- Eine Anforderung wechselt auf „Geplant“ oder „In Umsetzung“.
- Einzelne oder sämtliche Anforderungen werden als „Umgesetzt“ markiert.
- Eine Anforderung wird abgelehnt, zurückgestellt oder archiviert.
- Die letzte offene Anforderung eines Releases wird abgeschlossen.
- Ein Release besitzt keine zugeordneten Anforderungen.

Auch Releases ohne Anforderungen müssen jederzeit manuell geplant, aktiviert oder abgeschlossen werden können.

## 2. Bedienung in der Oberfläche

Implementiere eine komfortable manuelle Statusverwaltung, analog zur bestehenden Anforderungsverwaltung.

Gewünscht sind:

- Button „Status ändern“ in der Detailansicht
- Sichtbare Statusleiste mit dem aktuellen Zustand
- Möglichkeit, jeden zulässigen Zielstatus manuell auszuwählen
- Statusänderungen unabhängig von der Anzahl und dem Bearbeitungsstand der Anforderungen
- Optional direktes Verschieben zwischen Kanban-Spalten, sofern sich dies mit Odoo-Bordmitteln konsistent umsetzen lässt

Die Bedienung soll für Releases und Meilensteine gleichermaßen funktionieren.

## 3. Fortschritt und Release-Status trennen

Die bisherigen Kennzahlen und Fortschrittsanzeigen sollen erhalten bleiben.

Dazu gehören:

- Anzahl zugeordneter Anforderungen
- Anforderungen nach Bearbeitungsstatus
- Anzahl bereits umgesetzter Anforderungen
- Prozentualer Fortschritt

Diese Werte werden weiterhin automatisch berechnet, beeinflussen jedoch nicht den Status des Releases oder Meilensteins.

**100 % umgesetzte Anforderungen bedeuten ausdrücklich nicht, dass ein Release veröffentlicht ist.**

Es können weitere, nicht im Anforderungsmanagement erfasste Entwicklungsarbeiten ausstehen.

Umgekehrt darf ein Release veröffentlicht werden, obwohl noch nicht alle zugeordneten Anforderungen umgesetzt wurden.

## 4. Bewusster Abschluss

Beim manuellen Statuswechsel auf „Veröffentlicht“ bzw. „Abgeschlossen“:

- Prüfe, ob noch nicht umgesetzte Anforderungen zugeordnet sind.
- Zeige gegebenenfalls einen Hinweis mit der Anzahl dieser Anforderungen.
- Ermögliche eine ausdrückliche Bestätigung des Abschlusses.
- Blockiere den Abschluss nicht grundsätzlich.
- Setze das tatsächliche Abschluss-/Veröffentlichungsdatum nur im Rahmen dieses bewussten Statuswechsels.
- Verändere keine Status oder tatsächlichen Veröffentlichungsdaten der zugeordneten Anforderungen.

Die Statusänderung soll im Chatter protokolliert werden.

Ein späteres Zurücksetzen oder erneutes Öffnen des Releases muss möglich bleiben. Historische Abschlussinformationen dürfen dabei nicht unbemerkt verloren gehen.

## 5. Tests und Regressionen

Ergänze insbesondere Tests für:

1. Entwurf → Geplant ohne zugeordnete Anforderungen
2. Geplant → Aktiv unabhängig vom Anforderungsfortschritt
3. Alle Anforderungen umgesetzt, Release bleibt trotzdem Aktiv
4. Release wird manuell veröffentlicht, obwohl noch offene Anforderungen existieren
5. Zuordnung und Entfernung von Anforderungen verändern den Releasestatus nicht
6. Statusänderungen sind im Chatter nachvollziehbar
7. Abschlusswarnung und ausdrückliche Bestätigung funktionieren
8. Statuswechsel nach erneuter Öffnung funktionieren ohne Datenverlust
9. Bestehende Releases und Meilensteine bleiben beim Modulupgrade erhalten

Führe die vorhandenen Installations-, Upgrade- und Regressionstests erneut aus.

## 6. Umsetzung

Untersuche zunächst, ob der derzeitige Status tatsächlich automatisch berechnet wird oder lediglich die manuelle Bedienmöglichkeit fehlt. Behebe die eigentliche Ursache, ohne unnötige Datenmodelländerungen vorzunehmen.

Implementiere die Korrektur für **Odoo 18 und Odoo 20**.

Erhalte bestehende Datensätze, technische IDs und alle bisherigen Funktionen der Releaseplanung.

Arbeite möglichst eigenständig, prüfe die lokale Browseroberfläche, aktualisiere die Projektdokumentation und erstelle nachvollziehbare Git-Commits.

Pushes auf die autorisierten Development-Branches sind erlaubt. Keine Änderungen an Staging oder Production.

---

## 7. Fortschrittsanzeige fachlich präzisieren

Die Fortschrittsanzeige innerhalb der Releaseplanung darf nicht den Eindruck vermitteln, dass sie den vollständigen Entwicklungsfortschritt eines Releases abbildet.

**Anpassungen:**

- Die bisherige Bezeichnung „Fortschritt“ durch **„Umgesetzte Anforderungen“** ersetzen.
- Die Kennzahl als `X von Y Anforderungen umgesetzt` darstellen, optional ergänzt um einen Prozentwert und Fortschrittsbalken.
- Weitere Bearbeitungsstatus (Geplant, In Umsetzung, Zurückgestellt usw.) bleiben separat nachvollziehbar.
- Bei Releases ohne zugeordnete Anforderungen keinen Fortschritt von 100 % anzeigen, sondern beispielsweise „Keine Anforderungen zugeordnet“.
- Die Darstellung muss unabhängig vom eigentlichen Releasestatus bleiben.

**Beispiel:**

Ein Release steht auf „Aktiv“ und zeigt:

**Umgesetzte Anforderungen: 8 von 8 (100 %)**

Das bedeutet ausschließlich, dass alle acht im Anforderungsmanagement erfassten Anforderungen umgesetzt wurden. Es bedeutet ausdrücklich **nicht**, dass die Entwicklung des gesamten Releases abgeschlossen ist.

Die Veröffentlichung bleibt eine separate, bewusste Entscheidung.

Berücksichtige diese Unterscheidung auch in Tooltips, Beschriftungen, Kanban-Karten und zukünftigen Dashboard-Auswertungen.

Implementiere die Anpassung für Odoo 18 und Odoo 20 und ergänze entsprechende Regressionstests.
