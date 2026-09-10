# 🚒 JF-Manager

**JF-Manager** ist eine selbst gehostete, webbasierte Verwaltungsanwendung für Jugendfeuerwehren.  
Sie bündelt Mitgliederverwaltung, Termine, Anwesenheiten, Betreuer, Warteliste, Dokumente, Statistiken, To-Dos, Vorfall-/Unfalldokumentation, Benachrichtigungen und Backups in einer für Desktop und Mobilgeräte geeigneten Oberfläche.

**Aktuelle stabile Version: 1.0.0**

> JF-Manager ist ein unabhängiges Open-Source-Projekt. Es besteht keine offizielle Verbindung zu Feuerwehrverbänden, Behörden oder den in der Anwendung verlinkten externen Diensten.

Bei der Entwicklung von JF-Manager wurden KI-gestützte Werkzeuge unterstützend eingesetzt. Dies umfasst unter anderem die Unterstützung bei Konzeption, Programmierung, Fehlersuche und Dokumentation. Die Projektentscheidungen, Anforderungen und Verantwortung für die veröffentlichten Inhalte liegen beim Projektverantwortlichen.

## ✨ Funktionsumfang

### Mitgliederverwaltung
- Stammdaten von Mitgliedern mit Kontaktdaten und Erziehungsberechtigten
- Status wie aktiv, beurlaubt, Übergang oder Austritt
- Profilbilder und Datenschutz-/Einwilligungsangaben
- freiwillige Angaben zu Schule, Beruf und weiteren Organisationen
- besonders geschützter Bereich für sensible Gesundheitsangaben
- Beurlaubungen mit Zeitraum
- Abzeichen und Auszeichnungen, u. a. Jugendflamme und Leistungsspange
- Excel-Import mit Vorlage
- Excel-Export
- Stammdaten-Prüfbögen einzeln oder gesammelt als PDF
- konfigurierbare Tabellen, Filter und Seitengrößen

### Termine & Anwesenheit
- Übungen, Gruppenstunden und weitere Termine
- Kalender- und Listenansicht
- konfigurierbare Standardzeiten
- verpflichtende und freiwillige Gruppenstunden
- Anwesenheit für Mitglieder: anwesend, entschuldigt, unentschuldigt
- separate Betreuer-Anwesenheit
- Sammelaktionen für eine schnelle Erfassung
- beurlaubte Personen werden berücksichtigt
- freiwillige Gruppenstunden fließen nicht in Fehlserien und reguläre Anwesenheitsstatistiken ein
- DIVERA-Excel-Import mit Vorschau und Duplikaterkennung

### Dashboard & Suche
- persönliches Dashboard
- Widgets ein-/ausblenden und sortieren
- Kennzahlen, Termine, Geburtstage und Beurlaubungen
- Geschlechter-, Status- und Altersauswertungen
- globale Suche
- Schnellaufruf per `Strg/Cmd + K`
- responsive Oberfläche für Desktop, Tablet und Smartphone

### Betreuerverwaltung
- Stammdaten und Status
- Anwesenheit bei Terminen
- Fortbildungen und Qualifikationen
- Veranstalter, Unterrichtseinheiten und Gültigkeit
- Upload von Nachweisen

### Warteliste
- Interessenten erfassen und verwalten
- Kontaktstatus
- Excel-Export
- Übernahme eines Wartelisteneintrags als Mitglied

### To-Dos
- teaminterne Aufgaben
- Aufgaben, die mit Kindern oder Eltern geklärt werden müssen
- Zuweisung an einzelne, mehrere oder alle Mitglieder
- individuelle Erledigungsstände
- bei Terminen können Aufgaben für alle anwesenden betroffenen Mitglieder gesammelt erledigt werden
- Warnung vor dem Abschluss einer Anwesenheit bei noch offenen relevanten Aufgaben

### Vorfälle & Unfälle
- getrennte Dokumentation von Vorfällen und Unfällen
- Verknüpfung mit Terminen
- Auswahl beteiligter Mitglieder, Betreuer und Erziehungsberechtigter
- Zeugen und Freitextdokumentation
- unfallbezogene Angaben
- bewusste Meldung an konfigurierte Empfänger der Wehrführung
- rollenabhängige Sichtbarkeit und Bearbeitungsfristen

### Dokumente & Auswertungen
- Dokumentencenter
- Kontaktlisten und Geburtstagslisten als PDF
- Warteliste als PDF
- Betreuer-, Termin- und Anwesenheitsdaten als Excel
- Mitgliederstatistiken
- Monats-, Jahres- und personenbezogene Anwesenheitsauswertungen

### Benachrichtigungen
- automatische Hinweise auf Geburtstage
- Fehlserien und längere entschuldigte Abwesenheiten
- bevorstehendes Ende einer Beurlaubung
- E-Mail-Versand und Versandprotokoll
- optionale Web-Push-Benachrichtigungen über VAPID

### Rollen & Datenschutz
- Admin
- Jugendwart
- stellvertretender Jugendwart
- Betreuer
- Leserolle
- serverseitige Berechtigungsprüfung
- Gesundheitsdaten werden nicht in normalen Listen, Suchen und Standardexporten ausgegeben
- geschützte Mediendateien
- Audit-Protokoll für relevante Änderungen

### Backup & Wiederherstellung
- vollständiges ZIP-Backup direkt aus der Anwendung
- PostgreSQL-Dump im Custom-Format
- Mediendateien im Backup
- SHA-256-Prüfung
- Sicherheitsbackup vor einer Wiederherstellung
- Wiederherstellung über die laufende Anwendung
- **Backup kann bereits bei der Einrichtung einer neuen Instanz eingespielt werden**
- Backup wird vor dem Import geprüft; anschließend werden notwendige Django-Migrationen ausgeführt
- serverbezogene Secrets und Netzwerkparameter werden beim Umzug nicht blind überschrieben

### PWA
- als Progressive Web App installierbar
- Installationshinweise für Android und iOS/iPadOS
- Offline-Seite
- mobil optimierte Navigation

### System & Betrieb
- Systemstatus und Diagnose
- Test-E-Mail
- Docker Secrets für sensible Zugangsdaten
- vereinfachte HTTP-/HTTPS-Konfiguration
- Unterstützung für direkten HTTP-Betrieb, Cloudflare Tunnel und klassische Reverse Proxies
- Installations-Preflight
- Schutz vor unbeabsichtigtem PostgreSQL-Passwortwechsel bei bestehenden Datenvolumes

## 🧱 Technik

JF-Manager basiert unter anderem auf:

- Python / Django
- PostgreSQL 18
- Redis
- Celery
- Gunicorn
- Docker & Docker Compose

Die Anwendung wird vollständig über Docker Compose betrieben.

## 🚀 Schnellstart

Voraussetzungen sind ein Linux-Server mit aktuellem Docker und Docker Compose Plugin.

```bash
unzip jf-manager-v1.0.0.zip
cd jf-manager-v1.0.0

cp .env.example .env
bash setup.sh

docker compose build --no-cache
docker compose up -d
```

`bash setup.sh` ist bewusst der empfohlene Aufruf. Dadurch funktioniert die Installation auch dann, wenn ein ZIP-Programm das Unix-Ausführungsrecht von `setup.sh` nicht übernimmt.

Anschließend die während des Setups konfigurierte Adresse im Browser öffnen.

Eine ausführliche Anleitung befindet sich in **[INSTALLATION.md](INSTALLATION.md)**.

## 🆕 Ersteinrichtung

Auf einer leeren Datenbank führt JF-Manager zu `/setup/`. Dort stehen zwei Wege zur Verfügung:

**Neue Instanz einrichten** – Organisationsdaten und das erste Administratorkonto werden angelegt.

**Backup wiederherstellen** – ein vorhandenes JF-Manager-ZIP-Backup wird geprüft und auf der neuen Instanz eingespielt.

## 🌐 HTTP, HTTPS & Reverse Proxy

Für den normalen Betrieb werden im Wesentlichen zwei Parameter verwendet:

```env
JF_PUBLIC_URL=http://server.example:8000
JF_PROXY_MODE=none
```

Für Cloudflare Tunnel beispielsweise:

```env
JF_PUBLIC_URL=https://jfmanager.example.org
JF_PROXY_MODE=cloudflare
```

Unterstützte Proxy-Modi:

- `none`
- `cloudflare`
- `reverse-proxy`

JF-Manager leitet daraus Allowed Hosts, CSRF-Origin, Secure Cookies und Proxy-Verhalten ab. Forwarded-Header werden nur in einem ausdrücklich aktivierten Proxy-Modus vertraut.

## 💾 Datensicherung

Backups enthalten personenbezogene und möglicherweise besonders schützenswerte Daten. Sie sollten zusätzlich außerhalb des Servers gesichert, verschlüsselt und nur autorisierten Personen zugänglich gemacht werden.

Vor Updates sollte immer ein aktuelles vollständiges Backup erstellt werden.

## 🔄 Updates

Grundsätzlich:

```bash
docker compose down
bash setup.sh
docker compose build --no-cache
docker compose up -d
```

Vorher unbedingt ein Backup erstellen und die Release Notes bzw. das Changelog der Zielversion lesen.

## 🔐 Datenschutz & Verantwortung

JF-Manager kann personenbezogene Daten Minderjähriger sowie optionale Gesundheitsinformationen verarbeiten. Betreiber sind selbst dafür verantwortlich, die für ihren Einsatz geltenden Datenschutz-, Aufbewahrungs-, Berechtigungs- und Einwilligungsanforderungen zu prüfen und umzusetzen.

Eine öffentlich erreichbare produktive Installation sollte ausschließlich über HTTPS betrieben werden. Zugriff auf Backups, Server, Docker und Administrationskonten ist angemessen abzusichern.

## 🧪 Status von Version 1.0

Version 1.0.0 ist die erste stabile Veröffentlichung. Die Neuinstallation sowie die Wiederherstellung einer bestehenden Instanz aus einem JF-Manager-Backup wurden im Release-Candidate-Prozess praktisch getestet.

Fehlerberichte und nachvollziehbare Verbesserungsvorschläge sind willkommen.

## 🗺️ Weiterentwicklung

Für die 1.1-Entwicklung sind weitere Module vorgesehen. Größere neue Funktionen werden nicht rückwirkend in 1.0.x eingebaut; die 1.0.x-Linie ist primär für Fehlerbehebungen und kleinere Verbesserungen vorgesehen.

## 🤝 Mitwirken

Issues und Pull Requests sind willkommen. Bei Fehlerberichten bitte – ohne personenbezogene Daten oder Zugangsdaten – möglichst angeben:

- JF-Manager-Version
- Betriebssystem / Docker-Version
- Installationsart (HTTP, Cloudflare Tunnel, Reverse Proxy)
- relevante Logauszüge
- Schritte zum Reproduzieren

**Niemals Passwörter, Secret-Dateien, private VAPID-Schlüssel, vollständige `.env`-Dateien oder personenbezogene Daten in Issues veröffentlichen.**

## 📄 Lizenz

JF-Manager ist freie Open-Source-Software und wird unter **GNU Affero General Public License v3.0 or later (`AGPL-3.0-or-later`)** veröffentlicht.

Du darfst JF-Manager verwenden, untersuchen, verändern und weitergeben – unter den Bedingungen der AGPL. Wenn eine veränderte Version über ein Netzwerk für andere Nutzer bereitgestellt wird, muss diesen Nutzern der entsprechende Quellcode gemäß AGPL zugänglich gemacht werden.

Der vollständige Lizenztext befindet sich in [`LICENSE`](LICENSE).
