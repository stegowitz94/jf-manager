# JF-Manager 1.0.0 – First Stable Release 🚒

JF-Manager 1.0.0 ist die erste stabile Veröffentlichung der selbst gehosteten Verwaltungsanwendung für Jugendfeuerwehren.

## Highlights

- Mitglieder-, Betreuer- und Wartelistenverwaltung
- Termine und Anwesenheiten für Mitglieder und Betreuer
- Abzeichen, Fortbildungen und Beurlaubungen
- Dashboard, Statistiken, globale Suche und Dokumentencenter
- To-Dos mit Mitgliederbezug
- getrennte Vorfall- und Unfalldokumentation
- E-Mail- und optionale Web-Push-Benachrichtigungen
- Rollen- und Berechtigungssystem
- Audit-Protokoll
- PWA für Desktop und Mobilgeräte
- vollständiges PostgreSQL-/Medien-Backup und Wiederherstellung
- Wiederherstellung eines vorhandenen Backups bereits während der Ersteinrichtung
- Docker-Compose-Deployment mit dateibasierten Secrets
- direkte HTTP-Nutzung, Cloudflare Tunnel und klassische Reverse Proxies

## Installation

Siehe `INSTALLATION.md`.

Kurzfassung:

```bash
cp .env.example .env
bash setup.sh
docker compose build --no-cache
docker compose up -d
```

## Upgrade

Vor jedem Upgrade ein vollständiges Backup erstellen. Bestehende PostgreSQL-Secrets dürfen bei einer vorhandenen Datenbank nicht durch neu generierte Werte ersetzt werden. Beim Wechsel von einer älteren Installation auf das dateibasierte Secret-System die Hinweise in `INSTALLATION.md` beachten.

## Lizenz

JF-Manager 1.0.0 wird unter **GNU Affero General Public License v3.0 or later (`AGPL-3.0-or-later`)** veröffentlicht.
