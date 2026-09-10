from pathlib import Path
from urllib.parse import urlparse
from celery.schedules import crontab
import environ
BASE_DIR = Path(__file__).resolve().parents[2]
env = environ.Env(DJANGO_DEBUG=(bool, False), EMAIL_USE_TLS=(bool, True), EMAIL_USE_SSL=(bool, False))
environ.Env.read_env(BASE_DIR.parent / ".env")

def _secret(name, secret_file, default=""):
    """Prefer a Docker secret file, keep env fallback for upgrades."""
    configured_file = env(f"{name}_FILE", default=secret_file)
    path = Path(configured_file) if configured_file else None
    if path and path.is_file():
        value = path.read_text(encoding="utf-8").strip()
        if value:
            return value
    return env(name, default=default)

SECRET_KEY = _secret("DJANGO_SECRET_KEY", "/run/secrets/django_secret_key")
DEBUG = env.bool("DJANGO_DEBUG", default=False)

# RC3.1: one public URL controls host/CSRF/cookie security. Legacy Django variables
# remain additive expert overrides for upgrades and unusual deployments.
JF_PUBLIC_URL = env("JF_PUBLIC_URL", default="http://localhost:8000").strip().rstrip("/")
JF_SOURCE_CODE_URL = env("JF_SOURCE_CODE_URL", default="").strip()
JF_PROXY_MODE = env("JF_PROXY_MODE", default="none").strip().lower()
if JF_PROXY_MODE not in {"none", "cloudflare", "reverse-proxy"}:
    raise RuntimeError("JF_PROXY_MODE muss none, cloudflare oder reverse-proxy sein.")
_public = urlparse(JF_PUBLIC_URL)
if _public.scheme not in {"http", "https"} or not _public.hostname:
    raise RuntimeError("JF_PUBLIC_URL muss eine vollständige http:// oder https:// URL sein.")
_public_host = _public.hostname
ALLOWED_HOSTS = list(dict.fromkeys([_public_host, "localhost", "127.0.0.1"] + env.list("DJANGO_ALLOWED_HOSTS", default=[])))
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys([JF_PUBLIC_URL] + env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])))
DATA_UPLOAD_MAX_NUMBER_FIELDS = env.int("DJANGO_DATA_UPLOAD_MAX_NUMBER_FIELDS", default=20000)
BACKUP_STORAGE_DIR = env("BACKUP_STORAGE_DIR", default=str(BASE_DIR / "backups"))
BACKUP_TEMP_DIR = env("BACKUP_TEMP_DIR", default="/tmp/jf-manager-backups")
BACKUP_MAX_UPLOAD_SIZE = env.int("BACKUP_MAX_UPLOAD_SIZE", default=2 * 1024 * 1024 * 1024)
BACKUP_SAFETY_KEEP = env.int("BACKUP_SAFETY_KEEP", default=5)
INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "accounts", "core", "waitinglist.apps.WaitinglistConfig", "audit.apps.AuditConfig", "documents.apps.DocumentsConfig", "members.apps.MembersConfig", "activities.apps.ActivitiesConfig", "supervisors.apps.SupervisorsConfig", "reports.apps.StatisticsConfig", "notifications.apps.NotificationsConfig", "incidents.apps.IncidentsConfig", "todos.apps.TodosConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "core.setup_middleware.SetupRequiredMiddleware",
    "accounts.middleware.RoleAccessMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "audit.middleware.AuditMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "core.context_processors.external_links",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"
DATABASES = {"default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": env("POSTGRES_DB"), "USER": env("POSTGRES_USER"),
    "PASSWORD": _secret("POSTGRES_PASSWORD", "/run/secrets/postgres_password"), "HOST": env("DATABASE_HOST", default="db"),
    "PORT": env("DATABASE_PORT", default="5432"), "CONN_MAX_AGE": 60,
}}
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "de-de"
TIME_ZONE = env("DJANGO_TIME_ZONE", default="Europe/Berlin")
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = _secret("EMAIL_HOST_PASSWORD", "/run/secrets/smtp_password", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="Jugendfeuerwehr <noreply@example.org>")
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://redis:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://redis:6379/1")
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 300
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=False)
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=False)
TRUST_PROXY_HEADERS = JF_PROXY_MODE in {"cloudflare", "reverse-proxy"}
if TRUST_PROXY_HEADERS:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# Secure cookies follow the configured public URL, not DEBUG. This permits a safe
# first-run over HTTP and automatically hardens cookies when switching to HTTPS.
SESSION_COOKIE_SECURE = (_public.scheme == "https")
CSRF_COOKIE_SECURE = (_public.scheme == "https")

CELERY_BEAT_SCHEDULE = {
    "daily-jf-notifications": {
        "task": "notifications.tasks.daily_notifications",
        "schedule": crontab(hour=7, minute=0),
    },
}

WEBPUSH_VAPID_PUBLIC_KEY = env("WEBPUSH_VAPID_PUBLIC_KEY", default="")
WEBPUSH_VAPID_PRIVATE_KEY = _secret("WEBPUSH_VAPID_PRIVATE_KEY", "/run/secrets/vapid_private_key", default="")
WEBPUSH_VAPID_CLAIMS_EMAIL = env("WEBPUSH_VAPID_CLAIMS_EMAIL", default="mailto:admin@example.org")
