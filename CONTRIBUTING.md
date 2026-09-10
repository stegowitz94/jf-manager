# Zu JF-Manager beitragen

Beiträge sind willkommen. Für größere Änderungen empfiehlt sich zunächst ein Issue, damit Ziel und Umfang abgestimmt werden können.

## Entwicklung

1. Repository forken oder klonen.
2. Eine lokale `.env` aus `.env.example` erstellen.
3. `bash setup.sh` ausführen.
4. Container mit `docker compose build` und `docker compose up -d` starten.
5. Änderungen in einem eigenen Branch umsetzen.
6. Tests und Django-Systemcheck ausführen.

```bash
docker compose exec web python manage.py check
docker compose exec web python manage.py test
```

## Pull Requests

Pull Requests sollten einen klar abgegrenzten Zweck haben und beschreiben, was geändert wurde und wie die Änderung getestet wurde. Datenbankänderungen benötigen passende Django-Migrationen.

Bitte keine produktiven `.env`-Dateien, Secret-Dateien, Backups, Dumps, Mediendateien oder personenbezogenen Daten committen.

## Lizenz

Mit dem Einreichen eines Beitrags erklärst du dich damit einverstanden, dass dein Beitrag unter derselben Lizenz wie JF-Manager veröffentlicht wird: **AGPL-3.0-or-later**.
