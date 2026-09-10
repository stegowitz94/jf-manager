#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd); cd "$ROOT"

mkdir -p secrets
chmod 700 secrets 2>/dev/null || true
[ -f .env ] || { cp .env.example .env; echo "Neue .env aus .env.example angelegt."; }

get_env(){ awk -v k="$1" 'index($0,k"=")==1 {sub("^[^=]*=",""); v=$0} END {print v}' .env; }
set_env(){ key="$1"; value="$2"; tmp=".env.tmp.$$"; awk -v k="$key" -v v="$value" 'BEGIN{done=0} index($0,k"=")==1 {if(!done){print k"="v;done=1};next} {print} END{if(!done)print k"="v}' .env > "$tmp"; mv "$tmp" .env; }
random_secret(){ if command -v openssl >/dev/null 2>&1; then openssl rand -base64 48 | tr -d '\n'; else dd if=/dev/urandom bs=48 count=1 2>/dev/null | base64 | tr -d '\n'; fi; }

# A fixed Compose project name means an older JF-Manager directory can still own the
# same persistent DB volume. Never create a new DB password behind an existing volume.
DB_VOLUME_EXISTS=no
if command -v docker >/dev/null 2>&1 && docker volume inspect jf-manager_postgres_data >/dev/null 2>&1; then
  DB_VOLUME_EXISTS=yes
fi
if [ "$DB_VOLUME_EXISTS" = yes ] && [ ! -s secrets/postgres_password.txt ]; then
  cat >&2 <<'MSG'

FEHLER: Ein bestehendes JF-Manager-PostgreSQL-Volume wurde gefunden,
aber in diesem Verzeichnis fehlt das zugehörige PostgreSQL-Secret.

JF-Manager erzeugt absichtlich KEIN neues Passwort, da die bestehende
Datenbank dieses nicht kennen würde.

Wenn dies ein Upgrade ist: secrets/postgres_password.txt aus der bisherigen
Installation übernehmen.
Wenn dies bewusst eine komplett neue Testinstanz ist: zuerst das alte
Compose-Projekt samt Volumes gezielt entfernen (Datenverlust!) und setup.sh
erneut ausführen.
MSG
  exit 2
fi

write_secret(){ file="$1"; legacy="$2"; generate="$3"; path="secrets/$file"; [ -f "$path" ] && return 0; value=$(get_env "$legacy"); if [ -n "$value" ]; then printf '%s' "$value" > "$path"; elif [ "$generate" = yes ]; then random_secret > "$path"; else : > "$path"; fi; }
write_secret postgres_password.txt POSTGRES_PASSWORD yes
write_secret django_secret_key.txt DJANGO_SECRET_KEY yes
write_secret smtp_password.txt EMAIL_HOST_PASSWORD no
write_secret vapid_private_key.txt WEBPUSH_VAPID_PRIVATE_KEY no

# File-backed Compose secrets retain the source mode. The directory is 0700 so other
# host users cannot traverse it; files need read permission so non-root app containers
# can consume the bind-mounted secret files.
chmod 700 secrets
chmod 644 secrets/*.txt

if grep -Eq '^(POSTGRES_PASSWORD|DJANGO_SECRET_KEY|EMAIL_HOST_PASSWORD|WEBPUSH_VAPID_PRIVATE_KEY)=' .env; then
  tmp=".env.tmp.$$"; grep -Ev '^(POSTGRES_PASSWORD|DJANGO_SECRET_KEY|EMAIL_HOST_PASSWORD|WEBPUSH_VAPID_PRIVATE_KEY)=' .env > "$tmp"; mv "$tmp" .env
fi

# Migrate legacy network settings if needed.
if ! grep -q '^JF_PUBLIC_URL=' .env; then
  origin=$(get_env DJANGO_CSRF_TRUSTED_ORIGINS | cut -d, -f1)
  [ -n "$origin" ] || origin="http://localhost:8000"
  printf '\nJF_PUBLIC_URL=%s\n' "$origin" >> .env
fi
if ! grep -q '^JF_PROXY_MODE=' .env; then
  trust=$(get_env DJANGO_TRUST_PROXY_HEADERS)
  [ "$trust" = true ] && mode="reverse-proxy" || mode="none"
  printf 'JF_PROXY_MODE=%s\n' "$mode" >> .env
fi

normalize_url(){
  raw=$(printf '%s' "$1" | tr -d '\r' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
  scheme="$2"
  case "$raw" in
    http://*|https://*) printf '%s' "$raw" ;;
    *) printf '%s://%s' "$scheme" "$raw" ;;
  esac
}

if [ -t 0 ]; then
  echo; echo "Netzwerkmodus (Enter = bestehende Werte behalten)"
  echo "  1) Direkt / lokales HTTP"; echo "  2) HTTPS über Cloudflare Tunnel"; echo "  3) HTTPS über Reverse Proxy"
  printf "Auswahl: "; read choice || true
  case "${choice:-}" in
    1) printf "Adresse (z.B. 192.168.1.50:8000 oder http://server:8000): "; read url; [ -n "$url" ] && set_env JF_PUBLIC_URL "$(normalize_url "$url" http)"; set_env JF_PROXY_MODE none;;
    2) printf "Öffentliche Adresse (z.B. jfmanager.example.de): "; read url; [ -n "$url" ] && set_env JF_PUBLIC_URL "$(normalize_url "$url" https)"; set_env JF_PROXY_MODE cloudflare;;
    3) printf "Öffentliche Adresse (z.B. jfmanager.example.de): "; read url; [ -n "$url" ] && set_env JF_PUBLIC_URL "$(normalize_url "$url" https)"; set_env JF_PROXY_MODE reverse-proxy;;
  esac
fi

# Also repair a scheme-less value left by RC3.1, based on the selected proxy mode.
url=$(get_env JF_PUBLIC_URL)
mode=$(get_env JF_PROXY_MODE)
case "$url" in
  http://*|https://*) ;;
  "") echo "FEHLER: JF_PUBLIC_URL ist leer. Bitte setup.sh erneut ausführen." >&2; exit 3;;
  *) if [ "$mode" = none ]; then url=$(normalize_url "$url" http); else url=$(normalize_url "$url" https); fi; set_env JF_PUBLIC_URL "$url";;
esac

case "$mode" in none|cloudflare|reverse-proxy) ;; *) echo "FEHLER: JF_PROXY_MODE muss none, cloudflare oder reverse-proxy sein." >&2; exit 3;; esac
case "$url" in http://*|https://*) ;; *) echo "FEHLER: JF_PUBLIC_URL muss mit http:// oder https:// beginnen." >&2; exit 3;; esac
hostpart=${url#*://}; hostpart=${hostpart%%/*}
[ -n "$hostpart" ] || { echo "FEHLER: JF_PUBLIC_URL enthält keinen Host." >&2; exit 3; }
if [ "$mode" != none ] && [ "${url#https://}" = "$url" ]; then
  echo "FEHLER: Proxy-Modus '$mode' benötigt eine https://-URL." >&2; exit 3
fi

printf '\nJF-Manager Preflight\n'
printf '  ✓ PostgreSQL-Secret vorhanden\n'
printf '  ✓ Django-Secret vorhanden\n'
printf '  ✓ JF_PUBLIC_URL: %s\n' "$url"
printf '  ✓ Proxy-Modus: %s\n' "$mode"
[ "$DB_VOLUME_EXISTS" = yes ] && printf '  ✓ Bestehendes PostgreSQL-Volume erkannt; Secret wurde beibehalten\n'
printf '\nKonfiguration gültig.\nDanach: docker compose build --no-cache && docker compose up -d\n'
