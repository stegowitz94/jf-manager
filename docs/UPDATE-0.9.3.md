# Update auf JF-Manager 0.9.3

1. Bestehende `.env` sichern und in das neue Projektverzeichnis kopieren.
2. Stack neu bauen und starten:

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

3. Migrationen kontrollieren:

```bash
docker compose exec web python manage.py showmigrations communications core notifications
```

Neu erwartet:

- `communications.0001_initial`
- `communications.0002_default_templates`
- `core.0005_appsettings_scouting_reminder_days`
- `notifications.0003_usernotificationpreference_scouting`

4. Celery-Worker-Logs und Web-Logs prüfen:

```bash
docker compose logs --tail=200 web worker beat
```

Rundschreiben benötigen eine funktionierende SMTP-Konfiguration. Ohne SMTP können Entwürfe und PDFs trotzdem verwendet werden; E-Mail-Versuche werden als fehlgeschlagen protokolliert.
