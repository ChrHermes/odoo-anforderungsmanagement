# Auftrag: Autonome Erstimplementierung des Odoo-Anforderungsmanagements

Du bist Lead Developer für unsere neue interne Odoo-18-App „Anforderungsmanagement“.

Arbeite möglichst eigenständig und implementiere so viel wie technisch sinnvoll und überprüfbar möglich.

## Grundlage

Lies und berücksichtige vollständig:

- `AGENTS.md`
- `SPEC.md`
- `TECHNICAL_DESIGN.md`
- `IMPLEMENTATION.md`

Die Dokumente bilden die verbindliche Projektspezifikation. Die folgenden Anweisungen ergänzen die dort festgelegten Entwicklungs- und Freigaberegeln.

## Ziel

Implementiere möglichst den gesamten definierten MVP einschließlich der Helpdesk-Integration.

Beschränke dich ausdrücklich nicht auf das technische Grundgerüst oder den ersten Meilenstein.

Arbeite die Meilensteine M1 bis M5 nacheinander ab. Fahre nach jeder erfolgreich abgeschlossenen Etappe selbstständig fort, solange keine unüberwindbare Blockade besteht.

## Arbeitsweise

1. Analysiere zuerst Repository, Spezifikation, Odoo-18-Kompatibilität und verfügbare Testmöglichkeiten.
2. Erstelle einen internen Implementierungsplan mit überprüfbaren Zwischenschritten.
3. Entwickle die Anwendung mit nativen Odoo-Komponenten, Python und XML.
4. Implementiere die vereinbarten Funktionen vollständig und nicht nur als Platzhalter.
5. Schreibe automatisierte Tests für die wesentlichen Funktionen und Berechtigungen.
6. Führe alle verfügbaren Tests aus und behebe gefundene Probleme eigenständig.
7. Prüfe deine Änderungen kritisch auf Sicherheitsprobleme, Datenintegrität, Wartbarkeit und Odoo-Kompatibilität.
8. Dokumentiere technische Annahmen und verbleibende Einschränkungen.
9. Fahre nach abgeschlossenen Meilensteinen ohne Rückfrage mit dem nächsten fort.

Bevorzuge eine funktionierende, zuverlässig getestete Implementierung gegenüber oberflächlicher Vollständigkeit.

## Git und Versionierung

Du bist ausdrücklich berechtigt, innerhalb des Development-Branches eigenständig Git-Commits zu erstellen.

- Verwende den Branch `codex/initial-mvp`.
- Erstelle nachvollziehbare Commits nach abgeschlossenen Meilensteinen oder sinnvollen Teilabschnitten.
- Verwende aussagekräftige Commit-Messages.
- Prüfe vor jedem Commit den Git-Diff.
- Committe keine Zugangsdaten, Secrets, Datenbankkopien oder Logdateien mit sensiblen Informationen.
- Verändere keine bestehenden fremden Branches.
- Verwende kein Force-Push.
- Führe keine Merges nach `main`, `master`, `staging` oder `production` durch.

### Remote-Repository

Prüfe eigenständig, welche Git-Remotes konfiguriert sind und ob ein nicht-interaktiver Push möglich ist.

Wenn das Remote-Repository eindeutig identifiziert ist und die Authentifizierung funktioniert, darfst du deine Commits eigenständig in den dafür vorgesehenen Development-Branch pushen.

Versuche nach abgeschlossenen Meilensteinen einen Push, sofern die notwendigen Rechte vorhanden sind.

Falls Git-Pushes wegen Authentifizierung, Sandbox-Beschränkungen oder fehlender Rechte nicht möglich sind:

- Versuche keine Umgehung der Sicherheitsgrenzen.
- Verändere keine Git-Zugangsdaten oder globalen Authentifizierungseinstellungen.
- Arbeite lokal weiter.
- Dokumentiere den Grund und die erforderlichen manuellen Schritte.

Das Fehlen eines Remote-Zugriffs ist ausdrücklich kein Grund, die Implementierung abzubrechen.

## Odoo.sh und Sicherheit

- Development darf eigenständig genutzt werden, soweit Zugriffe vorhanden und freigegeben sind.
- Keine Änderungen auf Staging ohne Freigabe.
- Keine Änderungen auf Production ohne Freigabe.
- Keine Verwendung echter Kundendaten für Entwicklungstests.
- Keine unkontrollierten ausgehenden E-Mails.
- Keine Installation oder Änderung von produktiven Odoo-Modulen.
- Beachte insbesondere die serverseitigen Zugriffsbeschränkungen für gespeicherte Helpdesk-Ticketbeschreibungen.

## Qualitätssicherung

Prüfe insbesondere:

- Modulinstallation und Aktualisierung
- Datenmodelle und relationale Verknüpfungen
- Berechtigungen und Record Rules
- Hierarchische Produktkategorien
- Statusübergänge und Pflichtbegründungen
- Chatter, Follower und Aktivitäten
- Helpdesk-Ticketverknüpfungen
- Unveränderliche Ticket-Momentaufnahmen
- Automatische interne Ticketnotizen
- Zusammenführung und Archivierung von Duplikaten

Falls keine ausführbare Odoo-18-Instanz oder keine Enterprise-Module zur Verfügung stehen, führe die möglichen statischen und isolierten Tests aus. Kennzeichne nicht ausführbare Integrationstests ausdrücklich als ungeprüft.

## Dokumentation und Abschluss

Pflege während der Entwicklung eine Datei `DEVELOPMENT_REPORT.md`.

Dokumentiere:

- Implementierte Funktionen und Meilensteine
- Git-Commits und erfolgreiche Pushes
- Ausgeführte Tests und Ergebnisse
- Technische Entscheidungen
- Offene Probleme und Einschränkungen
- Konkrete nächste Schritte
- Noch notwendige manuelle Konfiguration auf Odoo.sh

Erstelle außerdem eine kurze Installations- und Testanleitung.

## Wichtig

Arbeite möglichst autonom. Stelle keine Rückfragen zu gewöhnlichen Implementierungsdetails.

Wenn ein Problem auftritt, analysiere es und versuche eine fachlich und technisch saubere Lösung.

Stoppe nicht nach einer einzelnen erfolgreichen Teilaufgabe. Bearbeite den nächsten geplanten Schritt, solange sinnvoller Fortschritt möglich ist.

Nimm niemals an, dass ein Test erfolgreich war, wenn du ihn nicht tatsächlich ausführen konntest.

Beginne jetzt mit der vollständigen technischen Umsetzung.