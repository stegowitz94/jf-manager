# Architektur
- Django 5.2 LTS, modularer Monolith
- PostgreSQL 18 mit Volume unter `/var/lib/postgresql`
- Redis als Broker/Cache-Grundlage
- Celery Worker und Beat für spätere Benachrichtigungen
- Gunicorn als Application Server
- WhiteNoise für statische Dateien im ersten Meilenstein
- Benutzerdefiniertes User-Modell ist vor der ersten Migration vorhanden
