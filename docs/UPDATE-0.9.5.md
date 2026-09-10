# Update auf JF-Manager 0.9.5

## Änderung

Das optionale Kommunikationsmodul mit Rundschreiben, Vorlagen und Versandhistorie wurde entfernt. Automatische Benachrichtigungen aus dem Modul `notifications` bleiben aktiv.

## Update

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

Eine neue Datenbankmigration ist nicht erforderlich. Bereits vorhandene Tabellen des früheren Kommunikationsmoduls werden bewusst nicht automatisch gelöscht.
