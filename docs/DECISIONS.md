# Technische Entscheidungen

## D001 – Autorität und Offline-Implementierung (21.10.2026)

SPEC-Fachregeln bleiben verbindlich. Der aktuelle Auftrag gestattet bei fehlendem Enterprise-Zugriff statische/isolierte Entwicklung über M1 hinaus. Entsprechender Code gilt als implementiert, aber nicht als freigegeben. Insbesondere M3-Vertraulichkeits-/Mailgate und M5-Enterprise-Abnahme dürfen dadurch nicht als bestanden ausgewiesen werden.

## D002 – Private Ticketquellen (21.10.2026)

Keine App-ACL für Rohquellen und keine gespeicherte, allgemein lesbare Snapshot-Kopie. Zugriff ausschließlich über einen schmalen autorisierten Anzeigeweg, der zuerst Anforderungsrechte und die aktuellen Ticketrechte im Benutzerkontext prüft. Keine persistierten Transient-Snapshotansichten, die nach Rechteentzug weiter lesbar wären.

## D003 – Helpdesk-Anbindung ohne erfundene View-IDs (21.10.2026)

Da installierte Enterprise-/Custom-Views fehlen, werden native an `helpdesk.ticket` gebundene Aktionen verwendet. Sie sind im Aktionenmenü des Tickets sichtbar und benötigen keine ungeprüften Inheritance-Anker. Ein zusätzlicher Formular-Headerbutton darf erst nach Inspektion der echten Views ergänzt werden. Navigation zeigt verknüpfte Anforderungen mit Status in einer eigenen nativen Liste.

## D004 – Konservative Vorgaben (21.10.2026)

Letztes Veröffentlichungsdatum bleibt bei Rückwärtsübergängen erhalten. „Zuletzt aktualisiert“ bedeutet 30 Tage. Kundenorganisationen werden über `commercial_partner_id` dedupliziert. Stammdatenlöschung wird durch Archivierung ersetzt. Seed-Datensätze sind `noupdate`. Kein automatisches Kopieren von Ticketanhängen oder Ticketpriorität.

## D005 – Interne Helpdesk-Notizen ohne Benachrichtigungspipeline (21.10.2026)

Die private Übergangsmethode legt native `mail.message`-Notizen mit `mail.mt_note`, festem Modell, verknüpften Ticket-IDs, handelndem Autor und escaped Inhalt an. Sie ruft bewusst keine Helpdesk-`message_post`-Hooks auf und setzt keine Empfänger. Das vermeidet automatische Wiederöffnung und die Mail-/Followerpipeline des Standard-Chatter. Kein öffentliches RPC für beliebige privilegierte Ticketnachrichten. Externe Custom-Automationen bleiben ein zwingender neutralisierter Enterprise-/Staging-Test.

## D006 – Kein privater Relations-Suchkanal (21.10.2026)

`gc.requirement` erhält absichtlich kein öffentliches One2many auf private Quellen: relationale Suchdomains können fremde Modell-ACLs umgehen und Snapshot-Inhalte als Suchorakel verwenden. Ein schmaler RPC-Adapter liefert nur aktuell autorisierte Einträge. Native Quellenanzeige: Transient-Wizard mit ausschließlich nicht gespeichertem HTML; Leseformatierung und Export invalidieren den Anzeigecache, damit ein Rechteentzug auch innerhalb derselben Transaktion wirksam ist. Aggregatberechnung nutzt eng begrenztes sudo ohne Ticketdetails auszugeben.

## D007 – Verlustfreie Archivierung trotz Odoo-Standard (21.10.2026)

Im echten Odoo-18-Community-Code löschen `mail.activity.mixin.write` und `toggle_active` Aktivitäten beim Archivieren. Der Merge-Test hat dies nachgewiesen. Für Anforderungen ruft `toggle_active` deshalb die normale Model-Implementierung auf; der geprüfte Schreibpfad setzt bei Archivierung einen ausschließlich erhaltenden Kontext für `mail.activity.unlink`. Dieser überspringt nur Anforderungsaktivitäten nach bestehender Rechteprüfung, gewährt keine Rechte und ändert keine Aktivitäten anderer Modelle. Manuelles Erledigen bleibt möglich und getestet.

## D008 – Merge und Wiederherstellung (21.10.2026)

Quell-/Zielrechte werden vor Zeilensperren geprüft; mutiert wird ausschließlich per ORM. Beide Datensätze müssen aktiv und noch nicht zusammengeführt sein. Fehlende Ticketquellen werden mit Originalprovenienz kopiert; Überschneidungen bleiben an beiden Originalen. Anhänge/Chatter/Aktivitäten bleiben am Original und sind über „Erhaltene Originale“ zugänglich. Titel/Klassifikation/Status des Ziels bleiben führend, auch bei produktübergreifender manueller Entscheidung. Wiederherstellen eines Merge-Originals ist erlaubt, entfernt aber niemals den permanenten Redirect. Kettennavigation folgt zum aktuellen Überlebenden; direkte Redirect-Manipulation und erneutes Zusammenführen derselben Quelle sind gesperrt.
