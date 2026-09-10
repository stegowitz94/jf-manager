# Update auf JF-Manager 0.9.6

Version 0.9.6 ergänzt eine vollständige Backup- und Wiederherstellungsfunktion für Administratoren.

## Update

1. Die vorhandene `.env` in das neue Projektverzeichnis kopieren.
2. Container und Images neu erstellen:

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

Der vollständige Neubau ist erforderlich, weil im Web-Image die PostgreSQL-18-Werkzeuge `pg_dump` und `pg_restore` ergänzt wurden.

## Backup-Speicher

Docker Compose legt das neue Volume `backup_data` an. Dort bleiben die automatischen Sicherheitsbackups erhalten, die vor einer Wiederherstellung erstellt werden.

Optional in `.env`:

```env
BACKUP_STORAGE_DIR=/app/backups
BACKUP_TEMP_DIR=/tmp/jf-manager-backups
BACKUP_MAX_UPLOAD_SIZE=2147483648
BACKUP_SAFETY_KEEP=5
```

## Reverse Proxy

Der Reverse Proxy muss Uploads in der erwarteten Backupgröße erlauben. Bei NGINX beispielsweise:

```nginx
client_max_body_size 2G;
proxy_read_timeout 1800;
proxy_send_timeout 1800;
```

## Bedienung

Als Administrator: **System → Backup**.

Ein Backup enthält die vollständige PostgreSQL-Datenbank und alle Dateien aus dem Medien-Volume. Es enthält sensible personenbezogene Daten und sollte verschlüsselt sowie zugriffsgeschützt aufbewahrt werden.
