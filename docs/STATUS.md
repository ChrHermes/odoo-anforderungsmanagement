# Entwicklungsstand

## Auftrag und Plan

Autonome Erstimplementierung M1–M5 auf `codex/initial-mvp`; keine Staging-/Production-Aktionen. Der aktuelle Auftrag erlaubt bei fehlender Enterprise-Laufzeit statische und isolierte Prüfungen und verlangt die Kennzeichnung ungeprüfter Integrationstests. Sicherheitsgates bleiben Freigabeblocker; implementierter Code allein schließt keinen Meilenstein ab.

1. **Vorbereitung:** Spezifikationen lesen, Wissen initialisieren, Git/Dependencies/Testmöglichkeiten prüfen.
2. **M1:** Modelle, Stammdaten, Referenz, Gruppen, native Grundansichten; Modell-/XML-/ACL-Prüfungen.
3. **M2:** Workflow/Wizards, interne Zusammenarbeit, Suche und vollständige Oberfläche; negative ORM-Prüfungen.
4. **M3:** private Quellen, aktuelle Ticketrechte, Ticketaktionen, Kundenaggregation, interne Notizen; ausführliche Sicherheitsprüfungen.
5. **M4:** deterministische Duplikatvorschläge, bestätigte verlustfreie Zusammenführung, Archivierung; Historienprüfungen.
6. **M5:** kritischer Review, Installations-/Upgrade-/Leistungsprüfungen soweit verfügbar, Betriebs- und Fortsetzungsanleitung.

## Nachweise

- Alle vier verbindlichen Spezifikationsdateien vollständig gelesen.
- Branch und Remote geprüft; nicht-interaktives `git ls-remote` erfolgreich. Remote-Branch ungeschützt; tatsächliche Odoo.sh-Zuordnung und Schutz vor Staging/Production nicht bestätigt. Deployment bleibt gesperrt.
- Keine lokale Odoo-/Enterprise-Installation; Docker verfügbar. Enterprise-Quellcodezugriff nicht vorhanden (GitHub 404).
- Dokumentationsbasis vor Implementierungsbeginn gefüllt.

## Offen / nächster Schritt

M1 implementiert; 4 Odoo-18-TransactionCase-Tests im synthetischen Vertrag bestanden. Erster Lauf: 2 Testfehler (Exception-Erwartungen), korrigiert; Wiederholung: 0 Fehler. Installation/XML erfolgreich im isolierten Community-Vertrag. Enterprise-Installation und echter Upgrade-Nachweis bleiben offen. Als Nächstes M2.

Enterprise-Installation, bestehende Helpdesk-Customizations, echte Record Rules und Odoo.sh-Build bleiben nachzuweisen. Nutzeränderung `codex-task.md` nicht committen.
