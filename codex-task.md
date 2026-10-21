Du bist für die technische Erstimplementierung unserer eigenständigen Odoo-18-App „Anforderungsmanagement“ verantwortlich.

Lies zunächst vollständig:
- AGENTS.md
- SPEC.md
- TECHNICAL_DESIGN.md
- IMPLEMENTATION.md

**Ziel**

Implementiere einen möglichst vollständigen, funktionsfähigen MVP auf Grundlage der Spezifikation. Arbeite dabei weitgehend autonom und mit hohem Anspruch an Codequalität, Wartbarkeit und native Odoo-Integration.

**Arbeitsweise**

1. Analysiere zunächst das technische Konzept auf Widersprüche, fehlende Abhängigkeiten und Besonderheiten von Odoo 18.
2. Erstelle die notwendige Modulstruktur und implementiere die Anwendung anhand der Entwicklungsmeilensteine.
3. Arbeite die Meilensteine möglichst vollständig und nacheinander ab.
4. Schreibe automatisierte Tests für Datenmodelle, Berechtigungen, Workflows und Integrationen.
5. Führe verfügbare Tests aus und korrigiere auftretende Fehler eigenständig.
6. Erstelle nach erfolgreich abgeschlossenen Meilensteinen nachvollziehbare Git-Commits.
7. Fahre anschließend mit dem nächsten Meilenstein fort, solange keine kritische Blockade vorliegt.

**Technische Anforderungen**

- Verwende die nativen Odoo-18-Mechanismen und -Komponenten.
- Vermeide unnötige externe Python-Abhängigkeiten und eigene Frontend-Komponenten.
- Implementiere die Sicherheits- und Helpdesk-Berechtigungen ausdrücklich serverseitig.
- Berücksichtige die vereinbarten Grenzen zwischen Entwicklungs-, Staging- und Produktionsumgebung.
- Verwende keine echten Kundendaten für Tests.
- Erfinde keine erfolgreichen Testergebnisse. Dokumentiere Tests, die mangels Odoo-Laufzeitumgebung oder Enterprise-Modulen nicht ausführbar sind.

**Autonomie**

Triff bei nicht kritischen Implementierungsdetails selbstständig begründete Entscheidungen. Stelle keine Rückfragen, solange die Spezifikation eine sinnvolle Lösung zulässt.

Ändere bestehende fachliche Entscheidungen nicht eigenmächtig. Dokumentiere notwendige Abweichungen und Annahmen.

Führe keine Änderungen an Staging oder Production durch. Kein Merge in den Produktionsbranch und kein Deployment ohne ausdrückliche Freigabe.

**Abschluss**

Erstelle eine Datei `DEVELOPMENT_REPORT.md` mit:
- Abgeschlossenen und offenen Meilensteinen
- Implementierten Funktionen
- Durchgeführten Tests und ihren Ergebnissen
- Technischen Entscheidungen und Annahmen
- Bekannten Problemen und Einschränkungen
- Konkreten nächsten Schritten

Priorisiere funktionierenden und getesteten Code gegenüber einer nur oberflächlich vollständigen Implementierung.

Beginne jetzt mit der Umsetzung. Arbeite nach jedem abgeschlossenen Meilenstein selbstständig weiter, solange dies sinnvoll und sicher möglich ist.
