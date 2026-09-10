from __future__ import annotations

from django.views.decorators.cache import never_cache

import shutil
import os
from pathlib import Path

import django
import psycopg
import redis
from celery import current_app
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render
from django.views.static import serve

from activities.models import Activity
from members.models import Member
from supervisors.models import Supervisor
from accounts.permissions import is_admin as role_is_admin, is_leadership


def _is_admin(user) -> bool:
    return bool(user.is_authenticated and (user.is_superuser or user.role == "admin"))


def _format_bytes(value: int) -> str:
    size = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{value} B"


def _directory_size(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


@login_required
def dashboard(request):
    from datetime import date, timedelta
    import calendar
    from django.db.models import Count, Q
    from django.utils import timezone
    from activities.models import Attendance
    from members.models import Leave
    from notifications.models import NotificationLog
    from core.models import AppSettings, DashboardPreference, ExternalLink

    today = timezone.localdate()
    settings_obj = AppSettings.load()
    active_members = Member.objects.filter(activity_status=Member.ActivityStatus.ACTIVE).count()
    transition_members = Member.objects.filter(activity_status=Member.ActivityStatus.TRANSITION).count()
    leave_members = Member.objects.filter(activity_status=Member.ActivityStatus.ON_LEAVE).count()
    total_current_members = active_members + transition_members
    total_chart_members = total_current_members + leave_members
    gender_counts = {key: Member.objects.filter(activity_status__in=[Member.ActivityStatus.ACTIVE, Member.ActivityStatus.TRANSITION, Member.ActivityStatus.ON_LEAVE], gender=key).count() for key, _ in Member.Gender.choices}
    status_counts = {key: Member.objects.filter(activity_status=key).count() for key in (Member.ActivityStatus.ACTIVE, Member.ActivityStatus.TRANSITION, Member.ActivityStatus.ON_LEAVE)}

    def donut_segments(values, css_classes):
        """Return SVG-ready segments using strings with decimal points.

        pathLength=100 lets us use percentage values directly. Returning strings
        avoids Django's locale formatting (for example 85,0 in German), which
        would be invalid in SVG attributes.
        """
        total = sum(values)
        if total <= 0:
            return [{"css_class": "chart-empty", "dasharray": "100 0", "dashoffset": "0"}]
        segments = []
        offset = 0.0
        for value, css_class in zip(values, css_classes):
            percent = (value / total) * 100
            if percent > 0:
                segments.append({
                    "css_class": css_class,
                    "dasharray": f"{percent:.6f} {100 - percent:.6f}",
                    "dashoffset": f"{-offset:.6f}",
                })
            offset += percent
        return segments

    gender_segments = donut_segments(
        [
            gender_counts.get(Member.Gender.MALE, 0),
            gender_counts.get(Member.Gender.FEMALE, 0),
            gender_counts.get(Member.Gender.DIVERSE, 0),
            gender_counts.get(Member.Gender.NOT_SPECIFIED, 0),
        ],
        ["chart-male", "chart-female", "chart-diverse", "chart-unknown"],
    )
    status_segments = donut_segments(
        [
            status_counts.get(Member.ActivityStatus.ACTIVE, 0),
            status_counts.get(Member.ActivityStatus.TRANSITION, 0),
            status_counts.get(Member.ActivityStatus.ON_LEAVE, 0),
        ],
        ["chart-active", "chart-transition", "chart-leave"],
    )
    preference, _ = DashboardPreference.objects.get_or_create(user=request.user)
    from waitinglist.models import WaitingListEntry
    waiting_count = WaitingListEntry.objects.exclude(status__in=[WaitingListEntry.Status.ADMITTED, WaitingListEntry.Status.DECLINED]).count()
    favorite_links = ExternalLink.objects.filter(visible=True, favorite=True)
    active_supervisors = Supervisor.objects.filter(activity_status=Supervisor.ActivityStatus.ACTIVE).count()
    next_activities = Activity.objects.filter(starts_at__gte=timezone.now()).order_by("starts_at")[:5]
    open_attendance = Activity.objects.filter(attendance_completed=False, starts_at__lte=timezone.now()).count()
    birthdays = []
    horizon = today + timedelta(days=30)
    for obj, label in ((Member, "Mitglied"), (Supervisor, "Betreuer")):
        for person in obj.objects.exclude(birth_date=None):
            try:
                next_date = person.birth_date.replace(year=today.year)
            except ValueError:
                next_date = person.birth_date.replace(year=today.year, day=28)
            if next_date < today:
                try: next_date = next_date.replace(year=today.year + 1)
                except ValueError: next_date = next_date.replace(year=today.year + 1, day=28)
            if today <= next_date <= horizon:
                birthdays.append((next_date, person, label))
    birthdays.sort(key=lambda x: x[0])
    leaves_ending = Leave.objects.filter(planned_end_date__range=(today, today + timedelta(days=settings_obj.leave_notice_days))).select_related("member")[:8]

    def subtract_months(value, months):
        total = value.year * 12 + value.month - 1 - months
        year, month0 = divmod(total, 12)
        month = month0 + 1
        day = min(value.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    scouting_candidates = []
    eligible_statuses = [Member.ActivityStatus.ACTIVE, Member.ActivityStatus.TRANSITION]
    for person in Member.objects.filter(activity_status__in=eligible_statuses).order_by("birth_date"):
        try:
            eligible_date = subtract_months(person.birth_date.replace(year=person.birth_date.year + settings_obj.scouting_age_years), settings_obj.scouting_lead_months)
        except ValueError:
            birthday = person.birth_date.replace(year=person.birth_date.year + settings_obj.scouting_age_years, day=28)
            eligible_date = subtract_months(birthday, settings_obj.scouting_lead_months)
        days = (eligible_date - today).days
        if days >= -180:
            scouting_candidates.append({"member": person, "eligible_date": eligible_date, "days": days, "eligible": days <= 0, "soon": 0 < days <= 30})
    scouting_candidates.sort(key=lambda x: (not x["eligible"], abs(x["days"]) if x["eligible"] else x["days"]))
    scouting_candidates = scouting_candidates[:6]

    from audit.models import AuditEvent
    recent_changes = AuditEvent.objects.select_related("actor")[:6]
    today_tasks = []
    if open_attendance:
        today_tasks.append({"icon":"✓","title":f"{open_attendance} offene Anwesenheitsliste(n)","url":"/termine/"})
    if waiting_count:
        today_tasks.append({"icon":"⌛","title":f"{waiting_count} offene Wartelisteneinträge","url":"/warteliste/"})
    if leaves_ending:
        today_tasks.append({"icon":"◷","title":f"{len(leaves_ending)} Beurlaubung(en) enden bald","url":"/mitglieder/"})
    due_scouting = sum(1 for item in scouting_candidates if item["eligible"] or item["soon"])
    if due_scouting:
        today_tasks.append({"icon":"🚒","title":f"{due_scouting} Schnupperdienst-Hinweis(e)","url":"#schnupperdienst"})
    management_dashboard = is_leadership(request.user)
    if not management_dashboard:
        today_tasks = [task for task in today_tasks if not task["url"].startswith("/warteliste/")]
        recent_changes = []
    completed = Attendance.objects.filter(activity__attendance_completed=True, activity__starts_at__year=today.year).exclude(activity__activity_type=Activity.ActivityType.GROUP, activity__participation_mode=Activity.ParticipationMode.VOLUNTARY)
    total = completed.count(); present = completed.filter(status=Attendance.Status.PRESENT).count()
    attendance_rate = round(present / total * 100, 1) if total else 0
    # Monatliche Anwesenheitsentwicklung im aktuellen Jahr
    monthly_attendance = []
    max_month_rate = 100
    for month in range(1, 13):
        month_qs = completed.filter(activity__starts_at__month=month)
        month_total = month_qs.count()
        month_present = month_qs.filter(status=Attendance.Status.PRESENT).count()
        month_rate = round(month_present / month_total * 100, 1) if month_total else 0
        monthly_attendance.append({"month": month, "label": ["Jan","Feb","Mär","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"][month-1], "rate": month_rate, "rate_css": f"{month_rate:.1f}", "has_data": bool(month_total)})

    default_order = ["today","counts","gender","status","attendance_trend","scouting","next","birthdays","waiting","recent"]
    saved_order = [key for key in (preference.widget_order or []) if key in default_order]
    widget_order = saved_order + [key for key in default_order if key not in saved_order]
    order_map = {key: index + 1 for index, key in enumerate(widget_order)}
    context = {
        "management_dashboard": management_dashboard,
        "settings_obj": settings_obj, "active_members": active_members, "transition_members": transition_members, "leave_members": leave_members, "total_current_members": total_current_members, "total_chart_members": total_chart_members, "gender_counts": gender_counts, "status_counts": status_counts, "gender_segments": gender_segments, "status_segments": status_segments, "preference": preference, "waiting_count": waiting_count, "favorite_links": favorite_links, "active_supervisors": active_supervisors,
        "next_activities": next_activities, "open_attendance": open_attendance, "birthdays": birthdays[:8],
        "leaves_ending": leaves_ending, "attendance_rate": attendance_rate, "monthly_attendance": monthly_attendance, "has_attendance_data": any(item["has_data"] for item in monthly_attendance), "order_map": order_map, "current_year": today.year,
        "recent_notifications": NotificationLog.objects.all()[:5], "scouting_candidates": scouting_candidates, "today_tasks": today_tasks, "recent_changes": recent_changes,
    }
    return render(request, "core/dashboard.html", context)


def health(request):
    return JsonResponse({"status": "ok"})


@login_required
def protected_media(request, path):
    from accounts.permissions import is_leadership
    sensitive_prefixes=("supervisors/training_certificates/",)
    if path.startswith(sensitive_prefixes) and not is_leadership(request.user):
        return HttpResponseForbidden("Keine Berechtigung für diesen geschützten Nachweis.")
    return serve(request, path, document_root=settings.MEDIA_ROOT, show_indexes=False)


@login_required
def system_status(request):
    if not is_leadership(request.user):
        return HttpResponseForbidden("Dieser Bereich ist nur für Jugendwarte und Administratoren verfügbar.")

    checks: dict[str, dict[str, str | bool]] = {}

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            postgres_version = cursor.fetchone()[0]
        checks["database"] = {"ok": True, "label": "PostgreSQL", "detail": postgres_version}
    except Exception as exc:  # pragma: no cover - depends on runtime infrastructure
        checks["database"] = {"ok": False, "label": "PostgreSQL", "detail": str(exc)}

    try:
        redis_url = settings.CELERY_BROKER_URL
        redis_client = redis.Redis.from_url(redis_url, socket_connect_timeout=1, socket_timeout=1)
        redis_client.ping()
        checks["redis"] = {"ok": True, "label": "Redis", "detail": redis_url.split("@")[-1]}
    except Exception as exc:  # pragma: no cover
        checks["redis"] = {"ok": False, "label": "Redis", "detail": str(exc)}

    try:
        inspector = current_app.control.inspect(timeout=1)
        replies = inspector.ping() or {}
        worker_count = len(replies)
        checks["celery"] = {
            "ok": worker_count > 0,
            "label": "Celery Worker",
            "detail": f"{worker_count} Worker erreichbar" if worker_count else "Kein Worker erreichbar",
        }
    except Exception as exc:  # pragma: no cover
        checks["celery"] = {"ok": False, "label": "Celery Worker", "detail": str(exc)}

    try:
        executor = MigrationExecutor(connection)
        migration_plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        pending_migrations = len(migration_plan)
        checks["migrations"] = {
            "ok": pending_migrations == 0,
            "label": "Datenbankmigrationen",
            "detail": "Alle Migrationen angewendet" if pending_migrations == 0 else f"{pending_migrations} Migration(en) offen",
        }
    except Exception as exc:  # pragma: no cover
        checks["migrations"] = {"ok": False, "label": "Datenbankmigrationen", "detail": str(exc)}

    version_file = Path(settings.BASE_DIR) / "VERSION"
    app_version = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else "unbekannt"
    media_size = _directory_size(Path(settings.MEDIA_ROOT))
    disk = shutil.disk_usage(settings.BASE_DIR)

    checks["debug"] = {"ok": not settings.DEBUG, "label": "Produktionsmodus", "detail": "DEBUG deaktiviert" if not settings.DEBUG else "WARNUNG: DJANGO_DEBUG ist aktiviert"}
    direct_https = request.is_secure()
    forwarded_proto = request.META.get("HTTP_X_FORWARDED_PROTO", "").split(",")[0].strip().lower()
    cf_visitor = request.META.get("HTTP_CF_VISITOR", "")
    forwarded_https = forwarded_proto == "https" or '"scheme":"https"' in cf_visitor.replace(" ", "").lower()
    trusted_proxy = bool(getattr(settings, "TRUST_PROXY_HEADERS", False))
    https_ok = direct_https or (trusted_proxy and forwarded_https)
    if https_ok and trusted_proxy and forwarded_https:
        https_detail = "HTTPS über vertrauenswürdigen Proxy/Tunnel erkannt"
    elif https_ok:
        https_detail = "Direkte HTTPS-Verbindung erkannt"
    elif forwarded_https and not trusted_proxy:
        https_detail = "HTTPS-Header vorhanden, aber Proxy-Vertrauen ist deaktiviert (DJANGO_TRUST_PROXY_HEADERS=false)"
    else:
        https_detail = "Keine HTTPS-Verbindung erkannt"
    checks["https"] = {"ok": https_ok, "label": "HTTPS", "detail": https_detail}
    media_root=Path(settings.MEDIA_ROOT)
    try:
        media_root.mkdir(parents=True, exist_ok=True); test=media_root/".write-test"; test.write_text("ok"); test.unlink(); media_ok=True; media_detail="Media-Verzeichnis beschreibbar"
    except Exception as exc: media_ok=False; media_detail=str(exc)
    checks["media"]={"ok":media_ok,"label":"Dateispeicher","detail":media_detail}
    backup_root=Path(settings.BACKUP_STORAGE_DIR)
    try:
        backup_root.mkdir(parents=True, exist_ok=True); backup_ok=os.access(backup_root, os.W_OK); backup_detail=str(backup_root)
    except Exception as exc: backup_ok=False; backup_detail=str(exc)
    checks["backup"]={"ok":backup_ok,"label":"Backup-Verzeichnis","detail":backup_detail}
    checks["smtp"]={"ok": bool(settings.EMAIL_HOST and settings.EMAIL_HOST_USER and "console" not in settings.EMAIL_BACKEND), "label":"SMTP-Konfiguration", "detail": f"{settings.EMAIL_HOST}:{settings.EMAIL_PORT}" if settings.EMAIL_HOST else "Nicht konfiguriert"}

    smtp_configured = bool(settings.EMAIL_HOST and settings.EMAIL_HOST_USER)
    smtp_detail = (
        f"{settings.EMAIL_HOST}:{settings.EMAIL_PORT} · {'TLS' if settings.EMAIL_USE_TLS else 'ohne TLS'}"
        if smtp_configured
        else "Noch nicht vollständig konfiguriert"
    )

    context = {
        "checks": checks.values(),
        "app_version": app_version,
        "django_version": django.get_version(),
        "python_version": __import__("platform").python_version(),
        "psycopg_version": psycopg.__version__,
        "counts": {
            "members": Member.objects.count(),
            "supervisors": Supervisor.objects.count(),
            "activities": Activity.objects.count(),
        },
        "media_size": _format_bytes(media_size),
        "disk_free": _format_bytes(disk.free),
        "disk_total": _format_bytes(disk.total),
        "smtp_configured": smtp_configured,
        "smtp_detail": smtp_detail,
        "default_from_email": settings.DEFAULT_FROM_EMAIL,
    }
    return render(request, "core/system_status.html", context)


@login_required
def send_test_email(request):
    if not is_leadership(request.user):
        return HttpResponseForbidden("Dieser Bereich ist nur für Jugendwarte und Administratoren verfügbar.")
    if request.method != "POST":
        return redirect("core:system_status")

    recipient = (request.POST.get("recipient") or request.user.email or "").strip()
    if not recipient:
        messages.error(request, "Bitte eine Empfängeradresse angeben.")
        return redirect("core:system_status")

    try:
        sent = send_mail(
            subject="JF-Manager Testmail",
            message="Diese Testmail bestätigt, dass der E-Mail-Versand des JF-Managers funktioniert.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        if sent:
            messages.success(request, f"Testmail an {recipient} wurde versendet.")
        else:
            messages.error(request, "Der Mailversand wurde nicht bestätigt.")
    except Exception as exc:  # pragma: no cover - depends on SMTP runtime
        messages.error(request, f"Testmail konnte nicht versendet werden: {exc}")
    return redirect("core:system_status")


@never_cache
def service_worker(request):
    response = render(request, "core/service-worker.js", content_type="application/javascript")
    response["Service-Worker-Allowed"] = "/"
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


def manifest(request):
    return render(request, "core/manifest.webmanifest", content_type="application/manifest+json")


def offline(request):
    return render(request, "core/offline.html")


@login_required
def dashboard_settings(request):
    from core.models import DashboardPreference
    preference, _ = DashboardPreference.objects.get_or_create(user=request.user)
    widgets=[
      ("today","Heute und offene Aufgaben","show_today"),
      ("counts","Mitgliederzahlen","show_member_counts"),
      ("gender","Geschlechterdiagramm","show_gender_chart"),
      ("status","Statusdiagramm","show_status_chart"),
      ("attendance_trend","Anwesenheitsentwicklung","show_attendance_trend"),
      ("scouting","Schnupperdienst","show_scouting"),
      ("next","Nächste Termine","show_next_activities"),
      ("birthdays","Geburtstage","show_birthdays"),
      ("waiting","Warteliste","show_waiting_list"),
      ("recent","Letzte Änderungen","show_recent_changes"),
    ]
    if not is_leadership(request.user):
        widgets=[w for w in widgets if w[0] not in {"waiting","recent"}]
    if request.method=="POST":
        for key,label,field in widgets: setattr(preference,field,field in request.POST)
        posted=[]
        for index in range(len(widgets)):
            key=request.POST.get(f"order_{index}")
            if key and key not in posted: posted.append(key)
        preference.widget_order=posted
        preference.save(); messages.success(request,"Dashboard-Einstellungen wurden gespeichert."); return redirect("core:dashboard")
    current=[key for key in (preference.widget_order or []) if key in [w[0] for w in widgets]]
    current += [w[0] for w in widgets if w[0] not in current]
    by_key={w[0]:w for w in widgets}
    ordered=[{"key":k,"label":by_key[k][1],"field":by_key[k][2],"enabled":getattr(preference,by_key[k][2])} for k in current]
    return render(request,"core/dashboard_settings.html",{"preference":preference,"widgets":ordered})


@login_required
def global_search(request):
    from django.db.models import Q
    from waitinglist.models import WaitingListEntry
    q=(request.GET.get("q") or "").strip()
    results={"members":[],"supervisors":[],"waiting":[],"activities":[]}
    if q:
        results["members"]=Member.objects.filter(Q(first_name__icontains=q)|Q(last_name__icontains=q)|Q(city__icontains=q))[:12]
        if is_leadership(request.user):
            results["supervisors"]=Supervisor.objects.filter(Q(first_name__icontains=q)|Q(last_name__icontains=q))[:12]
            results["waiting"]=WaitingListEntry.objects.filter(Q(first_name__icontains=q)|Q(last_name__icontains=q)|Q(city__icontains=q))[:12]
        results["activities"]=Activity.objects.filter(Q(title__icontains=q)|Q(location__icontains=q))[:12]
    return render(request,"core/search.html",{"q":q,"results":results})


@login_required
def dashboard_layout_save(request):
    if request.method != "POST":
        return JsonResponse({"ok": False}, status=405)
    import json
    from core.models import DashboardPreference
    try:
        payload = json.loads(request.body.decode("utf-8"))
        order = [str(x) for x in payload.get("order", []) if x]
    except Exception:
        return JsonResponse({"ok": False, "error": "Ungültige Daten"}, status=400)
    pref, _ = DashboardPreference.objects.get_or_create(user=request.user)
    allowed = {"today","counts","gender","status","attendance_trend","scouting","next","birthdays","waiting","recent"}
    pref.widget_order = [x for x in order if x in allowed]
    pref.save(update_fields=("widget_order",))
    return JsonResponse({"ok": True})


@login_required
def table_preference_api(request, table_key):
    import json
    from core.models import UserTablePreference
    pref, _ = UserTablePreference.objects.get_or_create(user=request.user, table_key=table_key)
    if request.method == "GET":
        return JsonResponse({"visible_columns": pref.visible_columns, "column_order": pref.column_order, "page_size": pref.page_size, "filters": pref.filters})
    if request.method != "POST":
        return JsonResponse({"ok": False}, status=405)
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False, "error": "Ungültige Daten"}, status=400)
    if "visible_columns" in data: pref.visible_columns = [str(x) for x in data["visible_columns"]]
    if "column_order" in data: pref.column_order = [str(x) for x in data["column_order"]]
    if "page_size" in data:
        try: pref.page_size = min(100, max(10, int(data["page_size"])))
        except Exception: pass
    if "filters" in data and isinstance(data["filters"], dict): pref.filters = data["filters"]
    pref.save()
    return JsonResponse({"ok": True})


@login_required
def global_search_api(request):
    from django.db.models import Q
    from waitinglist.models import WaitingListEntry
    q=(request.GET.get("q") or "").strip()
    if len(q) < 2:
        return JsonResponse({"results": []})
    out=[]
    for x in Member.objects.filter(Q(first_name__icontains=q)|Q(last_name__icontains=q)|Q(city__icontains=q))[:6]:
        out.append({"type":"Mitglied","title":f"{x.first_name} {x.last_name}","detail":x.city or "","url":x.get_absolute_url()})
    if is_leadership(request.user):
        for x in Supervisor.objects.filter(Q(first_name__icontains=q)|Q(last_name__icontains=q)|Q(email__icontains=q))[:5]:
            out.append({"type":"Betreuer","title":f"{x.first_name} {x.last_name}","detail":x.email or "","url":x.get_absolute_url()})
        for x in WaitingListEntry.objects.filter(Q(first_name__icontains=q)|Q(last_name__icontains=q)|Q(city__icontains=q))[:5]:
            out.append({"type":"Warteliste","title":f"{x.first_name} {x.last_name}","detail":x.city or "","url":x.get_absolute_url()})
    for x in Activity.objects.filter(Q(title__icontains=q)|Q(location__icontains=q)).order_by("-starts_at")[:5]:
        out.append({"type":"Termin","title":x.title,"detail":x.starts_at.strftime("%d.%m.%Y"),"url":x.get_absolute_url()})
    return JsonResponse({"results":out[:18]})

@never_cache
def setup_restore(request):
    """Restore a JF-Manager backup on a fresh, not-yet-configured instance."""
    import tempfile
    from pathlib import Path
    from django.conf import settings as django_settings
    from django.contrib.auth import logout
    from core.backup_service import BackupError, inspect_backup, restore_backup
    from core.models import AppSettings

    if AppSettings.objects.filter(pk=1, setup_complete=True).exists():
        return redirect("core:dashboard" if request.user.is_authenticated else "login")
    if request.method != "POST":
        return redirect("core:setup")
    upload = request.FILES.get("backup_file")
    if not upload:
        messages.error(request, "Bitte eine JF-Manager-Backupdatei auswählen.")
        return redirect("core:setup")
    if not request.POST.get("acknowledge_restore"):
        messages.error(request, "Bitte bestätige die Wiederherstellung.")
        return redirect("core:setup")
    if upload.size > int(django_settings.BACKUP_MAX_UPLOAD_SIZE):
        messages.error(request, "Die Backupdatei überschreitet die erlaubte Maximalgröße.")
        return redirect("core:setup")
    if not upload.name.lower().endswith(".zip"):
        messages.error(request, "Es werden ausschließlich ZIP-Backups akzeptiert.")
        return redirect("core:setup")
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(prefix="jf-first-restore-", suffix=".zip", delete=False) as tmp:
            for chunk in upload.chunks():
                tmp.write(chunk)
            temp_path = Path(tmp.name)
        manifest = inspect_backup(temp_path)
        restored_manifest, _safety = restore_backup(temp_path)
        # Old backups receive current migrations during restore. 0007 marks an
        # upgraded pre-setup installation as configured. Ensure the flag also
        # exists for backups made around the setup transition.
        app_settings, _ = AppSettings.objects.get_or_create(pk=1)
        if not app_settings.setup_complete:
            app_settings.setup_complete = True
            app_settings.setup_completed_at = timezone.now()
            app_settings.save(update_fields=["setup_complete", "setup_completed_at"])
        logout(request)
        messages.success(request, f"Backup aus JF-Manager {restored_manifest.get('app_version', 'unbekannt')} wiederhergestellt. Bitte anmelden.")
        return redirect("login")
    except BackupError as exc:
        messages.error(request, f"Backup konnte nicht wiederhergestellt werden: {exc}")
    except Exception:
        messages.error(request, "Die Wiederherstellung ist fehlgeschlagen. Die Serverlogs enthalten weitere Details.")
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)
    return redirect("core:setup")


@never_cache
def setup_wizard(request):
    """One-time first-run setup. Existing/upgraded installations are never reopened."""
    from django.contrib.auth import get_user_model
    from django.db import transaction
    from django.utils import timezone
    from activities.models import ActivityTypeSetting
    from core.forms import OrganisationSetupForm, AdminSetupForm
    from core.models import AppSettings, ExternalLink

    existing = AppSettings.objects.filter(pk=1, setup_complete=True).first()
    if existing:
        return redirect("core:dashboard" if request.user.is_authenticated else "login")

    app_settings, _ = AppSettings.objects.get_or_create(pk=1)
    organisation_form = OrganisationSetupForm(request.POST or None, instance=app_settings, prefix="org")
    admin_form = AdminSetupForm(request.POST or None, prefix="admin")

    infrastructure = {
        "database": True,
        "redis": False,
        "smtp": bool(settings.EMAIL_HOST and settings.EMAIL_HOST_USER and "console" not in settings.EMAIL_BACKEND),
        "secrets": all(bool(getattr(settings, key, "")) for key in ("SECRET_KEY",)) and bool(settings.DATABASES["default"]["PASSWORD"]),
    }
    try:
        redis.Redis.from_url(settings.CELERY_BROKER_URL, socket_connect_timeout=1, socket_timeout=1).ping()
        infrastructure["redis"] = True
    except Exception:
        pass

    if request.method == "POST" and organisation_form.is_valid() and admin_form.is_valid():
        with transaction.atomic():
            obj = organisation_form.save(commit=False)
            obj.setup_complete = True
            obj.setup_completed_at = timezone.now()
            obj.save()
            data = admin_form.cleaned_data
            User = get_user_model()
            user = User.objects.create_user(
                username=data["username"], email=data["email"], password=data["password1"],
                first_name=data["first_name"], last_name=data["last_name"], role=User.Role.ADMIN,
                is_staff=True, is_superuser=True,
            )
            # Useful defaults; can be changed later in administration.
            from datetime import time
            ActivityTypeSetting.objects.get_or_create(activity_type="group", defaults={"default_start_time": time(17, 15), "default_end_time": time(18, 45)})
            # The BKS cloud is a Rheinland-Pfalz-specific convenience link.
            if obj.federal_state and obj.federal_state != "Rheinland-Pfalz":
                ExternalLink.objects.filter(name="BKS-Cloud").update(visible=False, favorite=False)
        from django.contrib.auth import login
        login(request, user)
        messages.success(request, "Ersteinrichtung abgeschlossen. Willkommen im JF-Manager.")
        return redirect("core:dashboard")

    return render(request, "core/setup.html", {
        "organisation_form": organisation_form,
        "admin_form": admin_form,
        "infrastructure": infrastructure,
        "smtp_host": settings.EMAIL_HOST,
        "smtp_port": settings.EMAIL_PORT,
        "default_from_email": settings.DEFAULT_FROM_EMAIL,
    })
