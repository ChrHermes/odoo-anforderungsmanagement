# Ergänzungsauftrag: App-Bezeichnung und Odoo-20-Kompatibilität

Erweitere den bisherigen MVP um folgende Anforderungen.

## 1. Benutzerfreundliche App-Bezeichnung

Der technische Modulname `gc_requirements` bleibt unverändert.

Der sichtbare Anwendungsname soll künftig **„Anforderungen“** lauten (vorläufiger Favorit; konfigurierbar bzw. später änderbar).

Prüfe und vereinheitliche:
- Manifest und App-Launcher
- Root-Menü und Fenstertitel
- Deutsche Menü- und Aktionsbezeichnungen
- Feldbeschriftungen, Status und Hinweise
- Deutsche Übersetzungen

Die Anwendung soll sich nahtlos in eine deutschsprachige Odoo-Umgebung einfügen. Technische Modellnamen und bestehende XML-IDs dürfen nicht unnötig verändert werden.

## 2. Unterstützung für Odoo 18 und 20

Erweitere die technische Zielsetzung um vollständige Kompatibilität mit Odoo 18 und Odoo 20.

Odoo 18 bleibt die primäre Entwicklungs- und Abnahmeplattform.

Prüfe zunächst, welche Änderungen für Odoo 20 erforderlich sind, insbesondere bei:
- ORM und Modellmethoden
- XML-Ansichten und Widgets
- Helpdesk-Integration
- Mail, Chatter, Followern und Aktivitäten
- Zugriffsrechten und Record Rules
- Manifest und Modulabhängigkeiten

Vermeide unnötig versionsabhängigen Code. Wo Unterschiede erforderlich sind, sollen diese nachvollziehbar und wartbar bleiben.

## 3. Kompatibilitäts- und Migrationstests

Erweitere die Teststrategie um:

1. Frische Installation unter Odoo 18
2. Modulupgrade unter Odoo 18
3. Frische Installation unter Odoo 20
4. Modulupgrade unter Odoo 20
5. Migration vorhandener Anforderungsdaten von Odoo 18 nach Odoo 20

Insbesondere müssen Anforderungsnummern, Kategorien, Ticketverknüpfungen, vertrauliche Momentaufnahmen, Anhänge, Chatter-Historien und Berechtigungen erhalten bleiben.

Die bisherigen Tests dürfen nicht entfernt oder abgeschwächt werden.

Eine Version darf erst als kompatibel bezeichnet werden, wenn entsprechende Laufzeittests erfolgreich waren. Synthetische Helpdesk-Tests ersetzen keine Enterprise-Abnahme.

## 4. Git und Dokumentation

Prüfe, ob separate Versionsbranches für Odoo 18 und 20 sinnvoll sind. Erstelle einen Vorschlag zur Branch- und Wartungsstrategie.

Entwickle die Odoo-20-Portierung gegebenenfalls in einem separaten Development-Branch. Verändere keine produktiven oder Staging-Branches.

Aktualisiere die Projektspezifikation, das technische Konzept, den Entwicklungsplan und das versionierte Projektgedächtnis.

Dokumentiere eindeutig:
- Verifizierte Odoo-18-Kompatibilität
- Verifizierte Odoo-20-Kompatibilität
- Noch nicht getestete Funktionen
- Notwendige Migrationsschritte
- Verbleibende Risiken

Arbeite innerhalb der vereinbarten Development-Berechtigungen möglichst eigenständig, erstelle sinnvolle Commits und pushe sie nach Möglichkeit in den vorgesehenen Development-Branch.

Keine Staging- oder Production-Änderungen ohne ausdrückliche Freigabe.