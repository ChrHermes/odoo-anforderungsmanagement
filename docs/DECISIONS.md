# Technische Entscheidungen

## D001 – Autorität und Offline-Implementierung (21.10.2026)

SPEC-Fachregeln bleiben verbindlich. Der aktuelle Auftrag gestattet bei fehlendem Enterprise-Zugriff statische/isolierte Entwicklung über M1 hinaus. Entsprechender Code gilt als implementiert, aber nicht als freigegeben. Insbesondere M3-Vertraulichkeits-/Mailgate und M5-Enterprise-Abnahme dürfen dadurch nicht als bestanden ausgewiesen werden.

## D002 – Private Ticketquellen (21.10.2026)

Keine App-ACL für Rohquellen und keine gespeicherte, allgemein lesbare Snapshot-Kopie. Zugriff ausschließlich über einen schmalen autorisierten Anzeigeweg, der zuerst Anforderungsrechte und die aktuellen Ticketrechte im Benutzerkontext prüft. Keine persistierten Transient-Snapshotansichten, die nach Rechteentzug weiter lesbar wären.

## D003 – Helpdesk-Anbindung ohne erfundene View-IDs (21.10.2026)

Da installierte Enterprise-/Custom-Views fehlen, werden native an `helpdesk.ticket` gebundene Aktionen verwendet. Sie sind im Aktionenmenü des Tickets sichtbar und benötigen keine ungeprüften Inheritance-Anker. Ein zusätzlicher Formular-Headerbutton darf erst nach Inspektion der echten Views ergänzt werden. Navigation zeigt verknüpfte Anforderungen mit Status in einer eigenen nativen Liste.

## D004 – Konservative Vorgaben (21.10.2026)

Letztes Veröffentlichungsdatum bleibt bei Rückwärtsübergängen erhalten. „Zuletzt aktualisiert“ bedeutet 30 Tage. Kundenorganisationen werden über `commercial_partner_id` dedupliziert. Stammdatenlöschung wird durch Archivierung ersetzt. Seed-Datensätze sind `noupdate`. Kein automatisches Kopieren von Ticketanhängen oder Ticketpriorität.
