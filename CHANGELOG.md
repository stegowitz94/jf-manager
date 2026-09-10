# Changelog

## 1.0.0 Stable

- Erste stabile Version von JF-Manager 1.0 auf Basis der erfolgreich getesteten RC3.2.
- Neueinrichtung und Wiederherstellung aus JF-Manager-ZIP-Backups.
- Vereinfachte HTTP/HTTPS-Konfiguration über `JF_PUBLIC_URL` und `JF_PROXY_MODE`.
- Installations-Preflight für URL, Proxy-Modus und Secrets.
- Schutz vor unbeabsichtigtem PostgreSQL-Passwortwechsel bei bestehenden Datenvolumes.
- Offizieller Setup-Aufruf: `bash setup.sh`, unabhängig vom Execute-Bit nach dem Entpacken.
- PWA-Service-Worker-Cache auf 1.0 Stable angehoben.
- Fachlicher Funktionsumfang gegenüber RC3.2 unverändert.

- Öffentliche Open-Source-Veröffentlichung unter AGPL-3.0-or-later vorbereitet.
- GitHub-Dokumentation, Security Policy, Contribution Guide und Issue-Templates ergänzt.
- Konfigurierbarer Quellcode-Link (`JF_SOURCE_CODE_URL`) für AGPL-konforme Netzwerkbereitstellungen ergänzt.

## 1.0.0 RC3.2

- Installations-Hardening nach realem RC3.1-Neuinstallationstest.
- `setup.sh` ergänzt fehlendes `http://` bzw. `https://` automatisch und validiert `JF_PUBLIC_URL`/`JF_PROXY_MODE` vor dem Start.
- Neuer verständlicher Preflight mit URL-, Proxy- und Secret-Prüfung.
- Schutz vor PostgreSQL-Passwortfehlern: Bei vorhandenem persistenten DB-Volume und fehlendem zugehörigen Secret wird abgebrochen, statt ein neues inkompatibles Passwort zu erzeugen.
- Bestehende Secrets werden bei erneutem Setup unverändert weiterverwendet.
- `setup.sh` wird im Release ausführbar ausgeliefert.
- PWA-Service-Worker-Cache auf RC3.2 angehoben.
- Fachlicher Funktionsumfang gegenüber RC3.1 unverändert; Neueinrichtung und Backup-Restore bleiben erhalten.


## 1.0.0 RC3.1
- Vereinfachte HTTP/HTTPS-Konfiguration über `JF_PUBLIC_URL` und `JF_PROXY_MODE`.
- Secure Session-/CSRF-Cookies werden automatisch aus dem URL-Schema abgeleitet.
- Proxy-Header werden nur in expliziten Proxy-Modi vertraut.
- Docker-Secret-Berechtigungen für nicht-root Container korrigiert; `secrets/` bleibt auf dem Host nicht durchsuchbar.
- Setup-Assistent kann auf einer frischen Instanz ein bestehendes JF-Manager-ZIP-Backup wiederherstellen.
- Restore prüft Backupformat, ZIP-Integrität, Datenbank-Prüfsumme und PostgreSQL-Dump vor dem Import und führt anschließend Migrationen aus.
- `setup.sh` bietet einen einfachen Netzwerkmodus-Dialog und migriert RC3-Netzwerkeinstellungen.


## 1.0.0 RC3

- Neuer einmaliger Ersteinrichtungsassistent für vollständig neue JF-Manager-Instanzen.
- Organisationsdaten sind nicht mehr auf eine konkrete Jugendfeuerwehr zugeschnitten; Name, Träger, Bundesland, Anschrift und Kontaktdaten werden beim Setup erfasst.
- Erstes Administratorkonto wird sicher im Web-Setup angelegt; kein Klartext-Adminpasswort in `.env` erforderlich.
- Bestehende Instanzen werden durch Migration automatisch als bereits eingerichtet markiert.
- Docker-Secrets für PostgreSQL-Passwort, Django Secret Key, SMTP-Passwort und privaten VAPID-Key.
- `setup.sh` erzeugt Secrets für Neuinstallationen und migriert bestehende RC2.1-Klartextwerte ohne Passwortwechsel.
- Secret-Werte haben Vorrang; Legacy-Umgebungsvariablen bleiben in Django als Update-Fallback lesbar.
- HTTPS-Diagnose hinter Cloudflare Tunnel/Reverse Proxy verbessert; Forwarded-Header werden nur bei `DJANGO_TRUST_PROXY_HEADERS=true` vertraut.
- BKS-Cloud wird bei neuen Installationen außerhalb Rheinland-Pfalz automatisch ausgeblendet.
- Neue RC3-Testcheckliste für Neuinstallation, Upgrade und Sicherheitsprüfung.

## 1.0.0 RC2.1

- To-Dos aus den einzelnen Mitgliederzeilen der Anwesenheit entfernt.
- Eigene Sektion „Offene To-Dos – Kinder / Eltern“ unterhalb der Anwesenheit.
- Sammel-To-Dos können mit „Alle Anwesenden erledigt“ in einem Schritt abgearbeitet werden.
- Einzelne Mitglieder bleiben über eine aufklappbare Liste gezielt erledigbar.
- Abschlusswarnung für offene To-Dos bleibt erhalten.

# 1.0.0 RC1

- Rollen & serverseitige Berechtigungen (Admin/Jugendwart/stv. Jugendwart/Betreuer/Leserolle)
- Betreuer: Termine & Anwesenheit, Mitglieder-Lesezugriff ohne Gesundheitsdaten, eigene Vorfälle/Unfälle 30 Tage sichtbar und 24 Stunden bearbeitbar
- Abzeichen & Auszeichnungen für Mitglieder
- Systemdiagnose und Produktionschecks erweitert
- iOS/iPadOS PWA-Installationshinweis
- Security-Hardening für Cookies, Referrer Policy, optionale HSTS-Konfiguration und Passwort-Mindestlänge 10
- Geschützte Fortbildungsnachweise
- Feature Freeze für RC-Testphase

# Changelog



## 0.9.12

- Desktop-Sidebar bündig ausgerichtet.
- Feste Icon-Spalte für alle internen und externen Menüeinträge.
- Einheitliche Textgrundlinie und Menüzeilenhöhe.
- Abschnittsüberschriften, Suchfeld und Benutzerbereich auf dasselbe Raster gesetzt.
- Account-Aktionen inklusive Abmelden einheitlich ausgerichtet.
- PWA-Cache auf Version 0.9.12 aktualisiert.

## 0.9.11

- Personenauswahl bei Vorfällen und Unfällen auf Desktop und Mobilgeräten vereinheitlicht.
- Native Mehrfachauswahl mit Strg-Taste durch Suchfeld mit Vorschlägen und Auswahl-Chips ersetzt.
- Mehrere Mitglieder, Betreuer und Erziehungsberechtigte können nacheinander hinzugefügt und einzeln entfernt werden.
- Tastaturbedienung mit Pfeiltasten, Enter und Escape ergänzt.
- Native Mehrfachauswahl bleibt als Fallback sichtbar, falls JavaScript nicht geladen werden kann.
- PWA-Cache auf Version 0.9.11 aktualisiert.

## 0.9.10
- Vorfalldokumentation und Unfalldokumentation fachlich und in der Oberfläche getrennt.
- Gemeinsamer Menüpunkt „Vorfälle & Unfälle“ mit Auswahl zwischen Vorfall und Unfall.
- Eigene Formulare für Vorfälle und Unfälle; Unfallfelder erscheinen nur noch in Unfallakten.
- Betroffene Mitglieder, Betreuer und Erziehungsberechtigte über Suchfelder mit Vorschlägen auswählbar.
- Mehrfachauswahl über Chips; ausgewählte Personen können direkt wieder entfernt werden.
- Erziehungsberechtigte werden in Vorschlägen zusammen mit dem zugehörigen Jugendlichen angezeigt.
- Bestehende Unfallakten werden per Migration automatisch in den neuen Dokumenttyp „Unfall“ übernommen.

## 0.9.9
- Neues geschütztes Modul „Vorfälle & Unfälle“ mit Terminverknüpfung, Beteiligten, Zeugen und Dokumentation.
- Unfall-spezifische Angaben und bewusster E-Mail-Versand an konfigurierbare Wehrführung.
- Gruppenstunden können verpflichtend oder freiwillig sein; freiwillige Gruppenstunden werden aus Anwesenheitsstatistik und Fehlserien ausgeschlossen.
- Betreuer-Fortbildungen/Qualifikationen mit Datum, Veranstalter, Gültigkeit, UE und Nachweis-Upload.

# Changelog

## 0.9.8
- Dashboard-Widgets können per Drag & Drop sortiert werden; Reihenfolge wird pro Benutzer gespeichert.
- Globale Suche als Schnellpalette mit Strg/Cmd + K und Live-Treffern.
- Persönliche Tabellen-Einstellungen für Mitglieder und Warteliste: sichtbare Spalten und Seitengröße.
- Mitglieder- und Wartelistenfilter werden pro Benutzer gemerkt und können zurückgesetzt werden.
- Pagination für Mitglieder und Warteliste; Seitengröße bei Betreuern konfigurierbar.
- Einheitliche Ladeanzeige für Formularaktionen und kleinere UI-Verbesserungen.
- Grundlage für weitere konfigurierbare Tabellen geschaffen.

# 0.9.7

- Betreuer-Anwesenheit pro Termin ergänzt.
- Betreuer können als anwesend, entschuldigt oder unentschuldigt erfasst werden.
- Beurlaubte Betreuer werden automatisch entschuldigt vorbelegt; ausgeschiedene Betreuer werden nicht angezeigt.
- Mobile Anwesenheitsansicht um einen separaten Betreuerbereich erweitert.
- Betreuer-Anwesenheiten sind getrennt von Mitgliederstatistik und Fehlserienlogik.


## 0.9.6

- Vollständiges ZIP-Backup aus der App heraus
- PostgreSQL-Sicherung im Custom-Format mit SHA-256-Prüfsumme
- Profilbilder, Logo und weitere Mediendateien im Backup enthalten
- Wiederherstellung mit Administratorkennwort und Sicherheitsphrase
- Automatisches Sicherheitsbackup vor jeder Wiederherstellung
- Gespeicherte Sicherheitsbackups können erneut heruntergeladen werden
- Admin-geschützter Menüpunkt „Backup“
- PostgreSQL-18-Clientwerkzeuge im Docker-Image


## 0.9.5

- Modul Kommunikation/Rundschreiben aus der Anwendung entfernt
- Kommunikationsvorlagen und Versandhistorie aus Navigation und URL-Konfiguration entfernt
- automatische Erinnerungen und persönliche Benachrichtigungen bleiben erhalten
- vorhandene Kommunikationstabellen werden aus Sicherheitsgründen nicht automatisch gelöscht
- PWA-Cache und Versionshinweise aktualisiert

## 0.9.4

- Dashboard-Kacheln kompakter und mit einheitlicheren Mindesthöhen dargestellt.
- Dashboard-Schnellzugriffe entfernt, da die Ziele bereits in der Navigation verfügbar sind.
- Versionshinweis mit größerem Abstand und besserer Textgliederung überarbeitet.
- Altersstruktur als echtes proportionales horizontales Balkendiagramm umgesetzt.
- Eintritte der letzten Jahre als Säulendiagramm umgesetzt.
- Nullwerte werden ohne irreführende Vollbalken dargestellt.
- PWA-Cache auf Version 0.9.4 aktualisiert.

## 0.9.2 – Freiwillige Zusatz- und Gesundheitsangaben

- Freiwillige Angaben zu Schule oder Arbeitgeber, Berufsausbildung und Berufsziel ergänzt.
- Freitextfeld für weitere Vereine und Organisationen ergänzt.
- Besonders geschützten Bereich für gesundheitliche Hinweise, Schwimmfähigkeit und Krankenversicherung ergänzt.
- Eigene Tabs „Schule & Beruf“ und „Gesundheit“ im Mitgliederprofil.
- Gesundheitsdaten erscheinen nicht in Mitgliederlisten, globaler Suche, Standard-PDFs oder Standard-Excel-Exporten.
- Mitgliederimport und Importvorlage um die neuen freiwilligen Felder erweitert.
- Standard-Excel-Export enthält nur die unkritischen Schul-/Berufs- und Organisationsangaben.
- Gesundheitsbereich im Formular und Admin visuell als sensibel gekennzeichnet.
- PWA-Cache auf Version 0.9.2 aktualisiert.

## 0.9.1 – Usability und Benutzerkonto

- Benutzerprofil mit persönlichen Angaben und Kontoinformationen
- Sichere Passwortänderung mit Prüfung des bisherigen Passworts
- Sitzung bleibt nach Passwortänderung erhalten
- Audit-Eintrag für Passwortänderungen ohne sensible Inhalte
- Sidebar-Navigation scrollt unabhängig vom festen Benutzerbereich
- Profil, Passwortänderung und Abmelden bleiben dauerhaft sichtbar
- Gruppierte Navigation und lokale Menüsuche
- Profil-Schnellzugriff in der mobilen unteren Navigation
- PWA-Cache auf Version 0.9.1 aktualisiert

# Changelog

## 0.9.0
- Schnupperdienst-Widget mit konfigurierbarem Alter und Vorlauf
- Heute-Widget mit offenen Aufgaben
- Mitgliederprofil mit Tabs für Stammdaten, Eltern, Anwesenheit, Dokumente und Historie
- Altersstruktur und Eintrittsentwicklung in Statistiken
- Letzte Änderungen als Dashboard-Widget
- Mobile Bottom-Navigation
- PWA-Cache aktualisiert


## 0.8.1
- Dashboard-Raster kompakter gestaltet
- Kreisdiagramme auf Desktop und Tablets nebeneinander angeordnet
- kleinere Diagramme und kompaktere Legenden
- Kennzahlenkarten und weitere Widgets platzsparender gestaltet
- kompakte Hinweisanzeige statt leerem Diagrammbereich, wenn noch keine Anwesenheitsdaten vorliegen
- responsive Umbruchgrenze für Dashboard-Widgets optimiert
- PWA-Cache für das Design-Update aktualisiert

## 0.8.0
- Dashboard-Widgets pro Benutzer ein-/ausblendbar und sortierbar
- animierte, klickbare SVG-Kreisdiagramme
- monatliche Anwesenheitsentwicklung auf dem Dashboard
- Logo und Kurzbezeichnung in den JF-Manager-Einstellungen
- Logo in Navigation und PDF-Dokumenten
- persönliche E-Mail-/Push-Einstellungen
- Web-Push-Geräteverwaltung und Test-Push über VAPID
- Erinnerung an Termine am Folgetag per E-Mail/Push
- erweitertes Dokumentencenter mit Kontakt-, Geburtstags- und Wartelisten-PDF
- PWA-Cache auf Version 0.8 aktualisiert

## 0.9.3
- Rundschreiben an Mitglieder, Erziehungsberechtigte, Betreuer und Warteliste
- Einzelversand per E-Mail ohne Offenlegung anderer Empfängeradressen
- Dokumentvorlagen mit mitgelieferten Standardvorlagen
- Rundschreiben als PDF mit Organisationslogo
- Versandhistorie mit Status und Fehleranzeige
- automatische Erinnerung vor dem Schnupperdienst
- Geburtstagsvorschau im Dashboard auf 30 Tage erweitert
- Mitgliederstatus-Diagramm zeigt keine Austritte mehr
- Geschlechterverteilung berücksichtigt beurlaubte Mitglieder und weist darauf hin

## 1.0.0 RC2
- Unfall: verletzte Mitglieder und Betreuer über suchbare Mehrfachauswahl; sonstige Verletzte separat.
- Zeitpunkt Elterninformation bei neuer Unfallakte mit aktueller Zeit vorbelegt.
- Neues To-Do-Modul: teamintern oder Kind/Eltern, Deadline, Zuständigkeit.
- Kind/Eltern-To-Dos für ein, mehrere oder alle Mitglieder mit individuellem Erledigungsstatus.
- Offene Punkte direkt in der Anwesenheit; Abschlusswarnung nur für anwesende Mitglieder.
