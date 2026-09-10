from __future__ import annotations

import tempfile
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from audit.models import AuditEvent

from .backup_service import (
    BackupError,
    create_download_backup,
    get_safety_backup,
    inspect_backup,
    list_safety_backups,
    restore_backup,
)

CONFIRMATION_TEXT = "BACKUP WIEDERHERSTELLEN"


def _is_admin(user) -> bool:
    return bool(user.is_authenticated and (user.is_superuser or user.role == "admin"))


def _forbidden():
    return HttpResponseForbidden("Dieser Bereich ist nur für Administratoren verfügbar.")


def _format_bytes(value: int) -> str:
    size = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{value} B"


@login_required
@require_http_methods(["GET"])
def backup_center(request):
    if not _is_admin(request.user):
        return _forbidden()
    safety_backups = list_safety_backups()
    return render(request, "core/backup_center.html", {
        "safety_backups": [
            {
                "filename": item.filename,
                "size": _format_bytes(item.size),
                "created_at": item.created_at,
            }
            for item in safety_backups
        ],
        "confirmation_text": CONFIRMATION_TEXT,
        "max_upload_size": _format_bytes(settings.BACKUP_MAX_UPLOAD_SIZE),
    })


@login_required
@require_POST
def backup_download(request):
    if not _is_admin(request.user):
        return _forbidden()
    try:
        path = create_download_backup()
    except BackupError as exc:
        messages.error(request, f"Backup konnte nicht erstellt werden: {exc}")
        return redirect("core:backup_center")

    try:
        AuditEvent.objects.create(
            actor=request.user,
            action="Backup erstellt",
            object_type="System",
            object_repr=path.name,
            detail="Vollständiges ZIP-Backup wurde zum Download erzeugt.",
            path=request.path,
        )
    except Exception:
        pass
    response = FileResponse(path.open("rb"), as_attachment=True, filename=path.name)
    response["Cache-Control"] = "no-store"
    # FileResponse keeps the handle open; remove the temp file after it is closed.
    original_close = response.close

    def close_and_remove():
        try:
            original_close()
        finally:
            path.unlink(missing_ok=True)

    response.close = close_and_remove
    return response


@login_required
@require_POST
def backup_restore(request):
    if not _is_admin(request.user):
        return _forbidden()

    upload = request.FILES.get("backup_file")
    password = request.POST.get("password", "")
    confirmation = request.POST.get("confirmation", "").strip()
    acknowledged = request.POST.get("acknowledge") == "on"

    if not upload:
        messages.error(request, "Bitte eine ZIP-Backupdatei auswählen.")
        return redirect("core:backup_center")
    if not request.user.check_password(password):
        messages.error(request, "Das Administratorkennwort ist nicht korrekt.")
        return redirect("core:backup_center")
    if confirmation != CONFIRMATION_TEXT or not acknowledged:
        messages.error(request, "Die Sicherheitsbestätigung ist unvollständig.")
        return redirect("core:backup_center")
    if upload.size > settings.BACKUP_MAX_UPLOAD_SIZE:
        messages.error(request, "Die Backupdatei überschreitet die erlaubte Maximalgröße.")
        return redirect("core:backup_center")
    if not upload.name.lower().endswith(".zip"):
        messages.error(request, "Es werden ausschließlich ZIP-Backups akzeptiert.")
        return redirect("core:backup_center")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(prefix="jf-upload-", suffix=".zip", delete=False) as temp:
            for chunk in upload.chunks():
                temp.write(chunk)
            temp_path = Path(temp.name)
        inspect_backup(temp_path)
        actor_id = request.user.pk
        restored_manifest, safety_backup = restore_backup(temp_path)
        from accounts.models import User
        restored_actor = User.objects.filter(pk=actor_id).first()
        try:
            AuditEvent.objects.create(
                actor=restored_actor,
                action="Backup wiederhergestellt",
                object_type="System",
                object_repr=upload.name[:255],
                detail=(
                    f"Backupversion {restored_manifest.get('app_version', 'unbekannt')} wiederhergestellt. "
                    f"Sicherheitsbackup: {safety_backup.name}"
                ),
                path=request.path,
            )
        except Exception:
            pass
    except BackupError as exc:
        messages.error(request, f"Wiederherstellung abgebrochen: {exc}")
        return redirect("core:backup_center")
    except Exception as exc:
        messages.error(request, f"Wiederherstellung fehlgeschlagen: {exc}")
        return redirect("core:backup_center")
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)

    # Session and users came from the backup. Re-authentication avoids stale session state.
    logout(request)
    messages.success(
        request,
        "Das Backup wurde wiederhergestellt. Bitte melde dich zur Sicherheit erneut an.",
    )
    return redirect("login")


@login_required
@require_http_methods(["GET"])
def safety_backup_download(request, filename: str):
    if not _is_admin(request.user):
        return _forbidden()
    try:
        path = get_safety_backup(filename)
    except BackupError as exc:
        raise Http404(str(exc)) from exc
    response = FileResponse(path.open("rb"), as_attachment=True, filename=path.name)
    response["Cache-Control"] = "no-store"
    return response
