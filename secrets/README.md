# JF-Manager Secrets

Die Dateien in diesem Verzeichnis werden mit `./setup.sh` erzeugt und **dürfen nicht in Git oder öffentliche ZIPs mit echten Werten übernommen werden**.

Erwartete Dateien:
- `postgres_password.txt`
- `django_secret_key.txt`
- `smtp_password.txt` (darf leer sein, solange SMTP nicht genutzt wird)
- `vapid_private_key.txt` (darf leer sein, solange Web Push nicht genutzt wird)

Auf Linux setzt `setup.sh` die Dateirechte auf `600`.
