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

## D009 – Reproduzierbare Prüfung und verbleibende Freigabe (21.10.2026)

Der versionsfixierte Community-Vertrag nutzt ein internes Docker-Netz ohne ausgehenden Netzpfad und ohne veröffentlichte Ports. Ein eigener Filestore überdauert Install-/Upgrade-Container, damit der Anhangserhalt tatsächlich geprüft wird. Der Testtreiber verlangt sowohl erfolgreichen Prozessstatus als auch positive Odoo-Testzusammenfassung; fehlende/fehlgeschlagene Tests können nicht als Erfolg durchlaufen. GitHub Actions prüft denselben Vertrag; dies ist ausdrücklich kein Odoo.sh-Enterprise-Build. Keine Runtime-/Deployment-Schutzkonfiguration außerhalb des Development-Teststacks ändern.

Das versionierte Testvertrag-Verzeichnis enthält absichtlich **kein** erkennbares `__manifest__.py`, sondern nur `manifest.py.in`. Erst der Testtreiber erzeugt das synthetische Modul in der Git-ignorierten `.local/contract-addons`-Laufzeitkopie. Damit kann eine rekursive Addonsuche im ausgecheckten Repository den Testvertrag nicht versehentlich als Enterprise-Helpdesk erkennen. Der statische Prüfer erzwingt diese Grenze.

## D010 – Aktive Klassifikation und interne Aktivitäten (21.10.2026)

Eine gespeicherte rekursive Selektierbarkeit blendet Bereiche unter archivierten Produkten/Vorfahren aus der Auswahl aus. Bestehende unveränderte Zuordnungen dürfen weiterhin gespeichert werden; echte neue Zuordnungen werden serverseitig auf den vollständigen aktiven Pfad geprüft. Aktivitätsassignees müssen aktuell interne berechtigte App-Benutzer sein; direkter ORM-Zugriff wird ebenso geprüft wie die UI.

## D011 – Name und native Konfiguration (22.10.2026)

Der Ergänzungsauftrag genehmigt **Anforderungen** als sichtbaren Namen bei unverändertem `gc_requirements`. Manifest, Rootmenü, Aktionen und Gruppen verwenden denselben Namen. Deutsche Originaltexte plus Übersetzungskatalog, keine neue Konfigurationsdatenhaltung. Menüänderung ist über native Administration möglich; Modulupgrades setzen versionierte Defaultlabels wieder. Dauerhafte Umbenennung zusammenhängend in Manifest/XML/Katalog ausliefern.

## D012 – Getrennte Versionslinien und ehrliche Nachweise (22.10.2026)

18 bleibt primär auf `codex/initial-mvp`; 20 wird separat auf `codex/20.0-port` mit nativem Manifest/APIs gepflegt. Gemeinsame Fixes gezielt übertragen, beide Suites separat ausführen. Vorgeschlagene spätere Wartungsbranches sind keine Hosting-/Promotionfreigabe. Bestehende Modelle, XML-IDs, Fach-/Sicherheitsregeln und Tests bleiben erhalten. Vertragsnachweise getrennt von Enterprise-Abnahme ausweisen.

## D013 – Major-Upgrade und lesende Inventur (22.10.2026)

Ein 18->20-Upgrade muss die gesamte Datenbank samt Filestore über den unterstützten Odoo-Upgradeweg migrieren. Eine neue 20er Datenbank oder `-u` auf derselben Majorversion beweist das nicht. Keine erfundene Coremigration oder Neucapture privater Quellen. Der administrative Shellprüfer vergleicht Daten-/Historien-/Berechtigungsinventuren einschließlich Originale und Ticketleser; Abweichungen stoppen die Abnahme, keine automatische Reparatur. Fehlender lizenzierter Upgradezugang bleibt ein offenes Gate.

## D014 – Beobachtete Odoo-20-APIs (22.10.2026)

Der 20er Port verwendet das tatsächlich installierte `ir.access` mit gruppierten Berechtigungen und globalen Einschränkungen statt der entfallenen ACL-/Rule-Modelle. Bestehende Sicherheits-XML-IDs bleiben erhalten; der native Gruppenscope wird ergänzt. Effektive Gruppen (`all_group_ids`), Action-`group_ids`, neue Mail-/Constraint-/Domain-/Gruppierungs-APIs und `raw.content` für physische Anhänge werden nativ verwendet. Die zusätzlich belegte Abhängigkeit `mail_tracking` erhält die aus `mail` ausgelagerten strukturierten Änderungswerte; diese werden nicht aus Tests entfernt. Keine Versionszweige im App-Sicherheitscode. Nur der administrative Inventurprüfer normalisiert beide Coreformate, prüft bestehende XML-ID-Ziele und echte Lesergebnisse. Die tatsächliche Core-/Sicherheitsmetadatenmigration bleibt ohne Enterprise-Upgradebestand offen.
