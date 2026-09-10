# Security Policy

## Unterstützte Versionen

Sicherheitskorrekturen werden grundsätzlich für die aktuelle stabile JF-Manager-Version bereitgestellt. Ältere Versionen sollten auf die jeweils aktuelle Stable-Version aktualisiert werden.

## Sicherheitslücken melden

Bitte Sicherheitslücken **nicht als öffentliches GitHub Issue veröffentlichen**, wenn dadurch eine ausnutzbare Schwachstelle, Zugangsdaten oder personenbezogene Daten offengelegt würden.

Nutze stattdessen die private Security-Advisory-Funktion des GitHub-Repositories ("Report a vulnerability"), sofern sie aktiviert ist. Der Repository-Betreiber sollte GitHub Private Vulnerability Reporting vor der Veröffentlichung aktivieren.

Bitte möglichst angeben:

- betroffene JF-Manager-Version,
- technische Beschreibung und Auswirkungen,
- nachvollziehbare Schritte zur Reproduktion,
- mögliche Gegenmaßnahmen, falls bekannt.

Keine realen Mitglieder-, Eltern- oder Betreuerdaten und keine Secrets mitsenden. Falls Testdaten nötig sind, ausschließlich synthetische Beispieldaten verwenden.

## Secrets

Folgende Inhalte gehören niemals in Issues, Pull Requests oder Screenshots:

- `.env` aus einer produktiven Installation,
- Dateien aus `secrets/*.txt`,
- SMTP- oder Datenbankpasswörter,
- private VAPID-Schlüssel,
- Backups oder Datenbank-Dumps,
- personenbezogene Daten.
