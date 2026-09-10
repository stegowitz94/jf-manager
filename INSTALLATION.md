# JF-Manager 1.0 – Installations- und Betriebsanleitung

Diese Anleitung beschreibt die Installation einer neuen JF-Manager-1.0-Instanz, die Wiederherstellung aus einem Backup und die wichtigsten Betriebsbefehle.

## 1. Voraussetzungen

Empfohlen wird ein Linux-Server oder eine Linux-VM mit:

- Docker Engine
- Docker Compose Plugin (`docker compose`)
- ausreichend persistentem Speicher für PostgreSQL, Medien und Backups
- einem aktuellen Webbrowser
- für den produktiven Internetbetrieb: Domain und HTTPS, z. B. über Cloudflare Tunnel oder einen Reverse Proxy

Prüfen:

```bash
docker --version
docker compose version
```

## 2. Dateien vorbereiten

Release herunterladen und in ein eigenes Verzeichnis entpacken:

```bash
unzip jf-manager-v1.0.0.zip
cd jf-manager-v1.0.0
```

Falls noch keine `.env` existiert:

```bash
cp .env.example .env
```

## 3. Setup ausführen

```bash
bash setup.sh
```

Der Aufruf über `bash` wird empfohlen, weil ZIP-Entpacker Unix-Ausführungsrechte nicht immer erhalten.

Der Setup-Assistent bereitet insbesondere die Secrets und die Netzwerkparameter vor und führt einen Preflight durch.

### Direkter HTTP-Test

Für einen internen Test kann JF-Manager beispielsweise direkt über Port 8000 erreichbar sein:

```env
JF_PUBLIC_URL=http://192.168.1.50:8000
JF_PROXY_MODE=none
```

oder:

```env
JF_PUBLIC_URL=http://server.example:8000
JF_PROXY_MODE=none
```

### Cloudflare Tunnel

```env
JF_PUBLIC_URL=https://jfmanager.example.org
JF_PROXY_MODE=cloudflare
```

### Anderer Reverse Proxy

```env
JF_PUBLIC_URL=https://jfmanager.example.org
JF_PROXY_MODE=reverse-proxy
```

Der vorgelagerte Proxy muss HTTPS korrekt terminieren und die üblichen Forwarded-Informationen passend setzen.

> Für eine öffentlich erreichbare Produktivinstallation wird HTTPS empfohlen.

## 4. Container bauen und starten

```bash
docker compose build --no-cache
docker compose up -d
```

Status prüfen:

```bash
docker compose ps
```

Logs:

```bash
docker compose logs --tail=100 web
docker compose logs --tail=100 db
```

## 5. Ersteinrichtung im Browser

Die in `JF_PUBLIC_URL` konfigurierte Adresse öffnen.

Bei einer leeren Instanz wird der Setup-Assistent angezeigt. Nun gibt es zwei Möglichkeiten.

### Variante A – neue Instanz

**Neue Instanz einrichten** auswählen und die Organisationsdaten sowie das erste Administratorkonto anlegen.

Danach steht die reguläre Anwendung zur Verfügung.

### Variante B – vorhandene Instanz wiederherstellen

**Vorhandene Instanz aus Backup wiederherstellen** auswählen und ein mit JF-Manager erzeugtes ZIP-Backup hochladen.

JF-Manager prüft das Backup vor dem Import. Danach werden Datenbank und Mediendaten wiederhergestellt und notwendige Migrationen ausgeführt.

Netzwerkparameter und die serverbezogenen Secrets des neuen Servers werden nicht einfach aus dem alten Backup übernommen. Dadurch kann eine Instanz beispielsweise von einem alten Server auf einen neuen Server oder auf eine neue Domain umziehen.

## 6. E-Mail konfigurieren

SMTP-Einstellungen werden über die vorgesehenen Konfigurationswerte gepflegt. Das SMTP-Passwort gehört in die dafür vorgesehene Secret-Datei und nicht in ein öffentliches Git-Repository.

Nach der Konfiguration kann unter **Systemstatus** eine Test-E-Mail ausgelöst werden.

Nach Änderungen an Umgebungsvariablen oder Secrets die betroffenen Container neu starten:

```bash
docker compose up -d --force-recreate
```

## 7. Optional: Web Push

Für Web Push werden ein VAPID-Schlüsselpaar und eine Claims-E-Mail benötigt.

Der **private VAPID-Key ist ein Secret** und darf nicht in GitHub, Screenshots oder Issues veröffentlicht werden.

Für Push und die reguläre PWA-Nutzung sollte die Anwendung über HTTPS erreichbar sein.

## 8. Backup erstellen

Administratoren finden die Backup-Funktion unter:

**System → Backup**

Das Backup enthält die PostgreSQL-Datenbank sowie hochgeladene Mediendateien. Backups können sensible personenbezogene Daten enthalten.

Empfehlung:

- regelmäßig Backups erzeugen
- mindestens eine Kopie außerhalb des JF-Manager-Servers aufbewahren
- externe Sicherungen verschlüsseln
- Wiederherstellung regelmäßig testen

## 9. Wiederherstellung einer laufenden Instanz

Die Wiederherstellung ist über **System → Backup** möglich. Vor dem eigentlichen Restore erstellt JF-Manager ein Sicherheitsbackup.

Eine Wiederherstellung ist ein administrativer Vorgang und sollte nur durchgeführt werden, wenn das verwendete Backup eindeutig zur gewünschten Instanz gehört.

## 10. Update

Vor jedem Update:

1. vollständiges JF-Manager-Backup erstellen,
2. `.env` und die serverbezogene Konfiguration sichern,
3. Changelog der Zielversion lesen.

Anschließend im neuen Release-Verzeichnis die bestehende Konfiguration gemäß Release-Hinweisen übernehmen und ausführen:

```bash
bash setup.sh
docker compose build --no-cache
docker compose up -d
```

Migrationen werden beim Start berücksichtigt.

**Nicht einfach neue PostgreSQL-Secrets erzeugen, wenn bereits ein Datenvolume existiert.** Der Installer enthält Schutzmechanismen hierfür; bestehende Secrets sollten bei Updates erhalten bleiben.

## 11. Nützliche Befehle

Containerstatus:

```bash
docker compose ps
```

Alle Logs:

```bash
docker compose logs --tail=200
```

Web-Logs:

```bash
docker compose logs --tail=200 web
```

Datenbank-Logs:

```bash
docker compose logs --tail=200 db
```

Container neu starten:

```bash
docker compose restart
```

Anwendung stoppen:

```bash
docker compose down
```

Anwendung wieder starten:

```bash
docker compose up -d
```

Migrationen kontrollieren:

```bash
docker compose exec web python manage.py showmigrations
```

Django-Systemcheck:

```bash
docker compose exec web python manage.py check
```

## 12. Wichtig: `docker compose down -v`

```bash
docker compose down -v
```

löscht die persistenten Docker-Volumes des Compose-Projekts und damit insbesondere die Datenbank.

**Diesen Befehl nicht für einen normalen Neustart oder ein Update verwenden.**

Er ist nur für Situationen gedacht, in denen eine Instanz bewusst vollständig zurückgesetzt werden soll und die Daten nicht mehr benötigt werden bzw. ein geprüftes Backup vorhanden ist.

## 13. Fehlerdiagnose

### `JF_PUBLIC_URL muss eine vollständige http:// oder https:// URL sein`

Prüfen:

```bash
grep -E 'JF_PUBLIC_URL|JF_PROXY_MODE' .env
docker compose config | grep -A2 -B2 JF_PUBLIC_URL
```

Beispiel:

```env
JF_PUBLIC_URL=http://server.example:8000
JF_PROXY_MODE=none
```

### `password authentication failed for user "jf_manager"`

PostgreSQL läuft dann häufig bereits mit einem bestehenden Datenvolume, während das konfigurierte Secret nicht zum Datenbankpasswort passt.

**Nicht das Volume löschen, wenn darin produktive Daten liegen.** Zuerst Backup-/Secret-Situation klären.

Logs:

```bash
docker compose logs --tail=100 db
```

### CSRF-Fehler bei HTTP

Prüfen, ob `JF_PUBLIC_URL` tatsächlich mit `http://` beginnt und `JF_PROXY_MODE=none` verwendet wird. JF-Manager leitet die Secure-Cookie-Einstellungen aus der öffentlichen URL ab.

### Anwendung startet nicht

```bash
docker compose ps
docker compose logs --tail=200 web
docker compose logs --tail=100 db
```

Keine Secrets oder personenbezogenen Daten in öffentliche Support-Anfragen kopieren.

## 14. Sicherheit vor Veröffentlichung im Internet

Vor einer öffentlichen Freigabe mindestens prüfen:

- HTTPS aktiv
- starkes Administratorkennwort
- Server und Docker aktuell
- SMTP-/Datenbank-/VAPID-Secrets nicht öffentlich zugänglich
- regelmäßige externe Backups
- nur benötigte Ports erreichbar
- Rollen und Benutzerkonten geprüft
- Datenschutz und Rechtsgrundlage für die gespeicherten Daten geklärt

## 15. GitHub-Deployment-Hinweis

Folgende Dateien bzw. Inhalte gehören **nicht** in das öffentliche Repository:

```text
.env
secrets/*.txt
Backups
Datenbank-Dumps
hochgeladene Mediendateien
echte Mitglieder-/Betreuerlisten
SMTP-Passwörter
private VAPID-Schlüssel
```

Vor dem ersten Push sollte eine passende `.gitignore` vorhanden sein.

## 16. Quellcode-Link bei AGPL-Betrieb

JF-Manager ist unter `AGPL-3.0-or-later` lizenziert. Für eine über das Netzwerk bereitgestellte Instanz kann die URL zum tatsächlich verwendeten Quellcode gesetzt werden:

```env
JF_SOURCE_CODE_URL=https://github.com/ORGANISATION/REPOSITORY
```

Ist die Variable gesetzt, zeigt JF-Manager in der Oberfläche einen **Quellcode**-Link an. Betreiber einer modifizierten Version müssen sicherstellen, dass der dort angebotene entsprechende Quellcode die Anforderungen der AGPL erfüllt.
