from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO

from django.conf import settings
from django.core.management import call_command
from django.db import connections

BACKUP_FORMAT = "jf-manager-backup-v1"
DATABASE_FILENAME = "database.dump"
MANIFEST_FILENAME = "manifest.json"
MEDIA_PREFIX = "media/"
README_FILENAME = "README.txt"


class BackupError(RuntimeError):
    """A user-facing backup or restore error."""


@dataclass(frozen=True)
class BackupInfo:
    path: Path
    filename: str
    size: int
    created_at: datetime


def _db_config() -> dict[str, str]:
    db = settings.DATABASES["default"]
    return {
        "name": str(db["NAME"]),
        "user": str(db["USER"]),
        "password": str(db["PASSWORD"]),
        "host": str(db.get("HOST") or "db"),
        "port": str(db.get("PORT") or "5432"),
    }


def _postgres_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PGPASSWORD"] = _db_config()["password"]
    return env


def _run(command: list[str], *, timeout: int = 900) -> None:
    try:
        result = subprocess.run(
            command,
            env=_postgres_env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        raise BackupError(
            "Das PostgreSQL-Sicherungsprogramm ist im Web-Container nicht installiert. "
            "Bitte das Docker-Image dieser Version neu bauen."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise BackupError("Der Datenbankvorgang hat das Zeitlimit überschritten.") from exc

    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "Unbekannter PostgreSQL-Fehler").strip()
        raise BackupError(detail[-3000:])


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _app_version() -> str:
    version_file = Path(settings.BASE_DIR) / "VERSION"
    return version_file.read_text(encoding="utf-8").strip() if version_file.exists() else "unbekannt"


def _safe_backup_name(prefix: str = "jf-manager-backup") -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{prefix}_{timestamp}.zip"


def _create_database_dump(target: Path) -> None:
    db = _db_config()
    connections.close_all()
    _run([
        "pg_dump",
        "--format=custom",
        "--compress=6",
        "--no-owner",
        "--no-acl",
        "--host", db["host"],
        "--port", db["port"],
        "--username", db["user"],
        "--file", str(target),
        db["name"],
    ])


def _iter_media_files() -> list[Path]:
    media_root = Path(settings.MEDIA_ROOT)
    if not media_root.exists():
        return []
    return [path for path in media_root.rglob("*") if path.is_file()]


def create_backup_zip(target: Path, *, reason: str = "Manuelles Backup") -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="jf-backup-") as tmp_name:
        tmp = Path(tmp_name)
        db_dump = tmp / DATABASE_FILENAME
        _create_database_dump(db_dump)
        media_files = _iter_media_files()
        manifest = {
            "format": BACKUP_FORMAT,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "app_version": _app_version(),
            "reason": reason,
            "database_sha256": _sha256(db_dump),
            "database_size": db_dump.stat().st_size,
            "media_file_count": len(media_files),
        }
        (tmp / MANIFEST_FILENAME).write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (tmp / README_FILENAME).write_text(
            "JF-Manager Backup\n\n"
            "Dieses Archiv enthält eine vollständige PostgreSQL-Datenbanksicherung "
            "und die hochgeladenen Mediendateien. Es enthält personenbezogene und "
            "gegebenenfalls gesundheitliche Daten und muss entsprechend geschützt aufbewahrt werden.\n",
            encoding="utf-8",
        )
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            archive.write(db_dump, DATABASE_FILENAME)
            archive.write(tmp / MANIFEST_FILENAME, MANIFEST_FILENAME)
            archive.write(tmp / README_FILENAME, README_FILENAME)
            media_root = Path(settings.MEDIA_ROOT)
            for media_file in media_files:
                relative = media_file.relative_to(media_root)
                archive.write(media_file, f"{MEDIA_PREFIX}{relative.as_posix()}")
    return target


def create_download_backup() -> Path:
    temp_dir = Path(settings.BACKUP_TEMP_DIR)
    temp_dir.mkdir(parents=True, exist_ok=True)
    return create_backup_zip(temp_dir / _safe_backup_name())


def create_safety_backup() -> Path:
    backup_dir = Path(settings.BACKUP_STORAGE_DIR)
    backup_dir.mkdir(parents=True, exist_ok=True)
    target = backup_dir / _safe_backup_name("vor-wiederherstellung")
    create_backup_zip(target, reason="Automatisches Sicherheitsbackup vor Wiederherstellung")
    _prune_safety_backups()
    return target


def _prune_safety_backups() -> None:
    keep = max(1, int(settings.BACKUP_SAFETY_KEEP))
    backups = list_safety_backups()
    for old in backups[keep:]:
        old.path.unlink(missing_ok=True)


def list_safety_backups() -> list[BackupInfo]:
    backup_dir = Path(settings.BACKUP_STORAGE_DIR)
    if not backup_dir.exists():
        return []
    result = []
    for path in backup_dir.glob("*.zip"):
        stat = path.stat()
        result.append(BackupInfo(
            path=path,
            filename=path.name,
            size=stat.st_size,
            created_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
        ))
    return sorted(result, key=lambda item: item.created_at, reverse=True)


def get_safety_backup(filename: str) -> Path:
    safe_name = Path(filename).name
    candidate = Path(settings.BACKUP_STORAGE_DIR) / safe_name
    if safe_name != filename or not candidate.is_file() or candidate.suffix.lower() != ".zip":
        raise BackupError("Das angeforderte Sicherheitsbackup wurde nicht gefunden.")
    return candidate


def _validate_zip_member(name: str) -> None:
    path = Path(name)
    if path.is_absolute() or ".." in path.parts:
        raise BackupError("Das Backup enthält einen unzulässigen Dateipfad.")


def inspect_backup(zip_path: Path) -> dict:
    if not zipfile.is_zipfile(zip_path):
        raise BackupError("Die hochgeladene Datei ist kein gültiges ZIP-Archiv.")
    try:
        with zipfile.ZipFile(zip_path) as archive:
            for info in archive.infolist():
                _validate_zip_member(info.filename)
            names = set(archive.namelist())
            if MANIFEST_FILENAME not in names or DATABASE_FILENAME not in names:
                raise BackupError("Das Archiv ist kein vollständiges JF-Manager-Backup.")
            manifest = json.loads(archive.read(MANIFEST_FILENAME).decode("utf-8"))
            if manifest.get("format") != BACKUP_FORMAT:
                raise BackupError("Das Backupformat wird von dieser Version nicht unterstützt.")
            bad_file = archive.testzip()
            if bad_file:
                raise BackupError(f"Das ZIP-Archiv ist beschädigt ({bad_file}).")
            return manifest
    except (zipfile.BadZipFile, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise BackupError("Das Backup konnte nicht gelesen werden.") from exc


def _extract_backup(zip_path: Path, target: Path) -> dict:
    manifest = inspect_backup(zip_path)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(target)
    dump_path = target / DATABASE_FILENAME
    if _sha256(dump_path) != manifest.get("database_sha256"):
        raise BackupError("Die Prüfsumme der Datenbanksicherung stimmt nicht überein.")
    # Ask pg_restore to parse the archive before touching the database.
    _run(["pg_restore", "--list", str(dump_path)], timeout=120)
    return manifest


def _restore_database(dump_path: Path) -> None:
    db = _db_config()
    connections.close_all()
    _run([
        "pg_restore",
        "--clean",
        "--if-exists",
        "--no-owner",
        "--no-acl",
        "--single-transaction",
        "--exit-on-error",
        "--host", db["host"],
        "--port", db["port"],
        "--username", db["user"],
        "--dbname", db["name"],
        str(dump_path),
    ], timeout=1800)
    connections.close_all()
    call_command("migrate", interactive=False, verbosity=0)
    connections.close_all()


def _restore_media(extracted_root: Path) -> None:
    source = extracted_root / "media"
    media_root = Path(settings.MEDIA_ROOT)
    media_root.mkdir(parents=True, exist_ok=True)
    rollback_dir = media_root / ".restore-rollback"
    if rollback_dir.exists():
        shutil.rmtree(rollback_dir)
    rollback_dir.mkdir()
    current_items = [item for item in media_root.iterdir() if item.name != rollback_dir.name]
    try:
        for item in current_items:
            shutil.move(str(item), str(rollback_dir / item.name))
        if source.exists():
            for item in source.iterdir():
                shutil.copytree(item, media_root / item.name) if item.is_dir() else shutil.copy2(item, media_root / item.name)
    except Exception:
        for item in [p for p in media_root.iterdir() if p.name != rollback_dir.name]:
            shutil.rmtree(item) if item.is_dir() else item.unlink(missing_ok=True)
        for item in rollback_dir.iterdir():
            shutil.move(str(item), str(media_root / item.name))
        raise
    finally:
        if rollback_dir.exists():
            shutil.rmtree(rollback_dir)


def restore_backup(zip_path: Path) -> tuple[dict, Path]:
    max_size = int(settings.BACKUP_MAX_UPLOAD_SIZE)
    if zip_path.stat().st_size > max_size:
        raise BackupError("Die Backupdatei überschreitet die erlaubte Maximalgröße.")

    with tempfile.TemporaryDirectory(prefix="jf-restore-") as tmp_name:
        extracted = Path(tmp_name)
        manifest = _extract_backup(zip_path, extracted)
        safety_backup = create_safety_backup()
        _restore_database(extracted / DATABASE_FILENAME)
        _restore_media(extracted)
        return manifest, safety_backup
