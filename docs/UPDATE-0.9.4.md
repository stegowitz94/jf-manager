# Update auf JF-Manager 0.9.4

1. Vorhandene `.env` sichern und in das neue Verzeichnis übernehmen.
2. Container neu bauen und starten:

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

Für Version 0.9.4 ist keine neue Datenbankmigration erforderlich. Browser bzw. PWA anschließend vollständig neu laden.
