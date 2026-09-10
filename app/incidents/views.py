import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import AccidentReportForm, IncidentReportForm
from .models import Incident
from accounts.permissions import is_leadership, is_supervisor, can_create_incident, incident_visible_to, incident_editable_by


def allowed(user):
    return can_create_incident(user)

def guard(request):
    return None if allowed(request.user) else HttpResponseForbidden("Keine Berechtigung für Vorfalls- und Unfallakten.")

def _initial(request):
    initial = {"occurred_at": timezone.localtime().strftime("%Y-%m-%dT%H:%M")}
    aid = request.GET.get("activity")
    if aid:
        initial["activity"] = aid
    return initial


@login_required
def incident_list(request):
    denied = guard(request)
    if denied:
        return denied
    qs = Incident.objects.select_related("activity", "created_by").filter(archived=False)
    if is_supervisor(request.user):
        cutoff = timezone.now() - timezone.timedelta(days=30)
        qs = qs.filter(created_by=request.user, created_at__gte=cutoff)
    return render(request, "incidents/list.html", {"incidents": qs})


@login_required
def create_choice(request):
    denied = guard(request)
    if denied:
        return denied
    return render(request, "incidents/create_choice.html", {"activity_id": request.GET.get("activity", "")})


@login_required
def incident_create(request):
    denied = guard(request)
    if denied:
        return denied
    form = IncidentReportForm(request.POST or None, initial=_initial(request))
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.created_by = request.user
        obj.record_type = Incident.RecordType.INCIDENT
        obj.save()
        form.save_m2m()
        messages.success(request, "Vorfall wurde dokumentiert.")
        return redirect(obj)
    return render(
        request,
        "incidents/form.html",
        {"form": form, "heading": "Vorfall dokumentieren", "record_type": "incident"},
    )


@login_required
def accident_create(request):
    denied = guard(request)
    if denied:
        return denied
    form = AccidentReportForm(request.POST or None, initial=_initial(request))
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.created_by = request.user
        obj.record_type = Incident.RecordType.ACCIDENT
        obj.kind = Incident.Kind.GENERAL
        obj.save()
        form.save_m2m()
        messages.success(request, "Unfall wurde dokumentiert.")
        return redirect(obj)
    return render(
        request,
        "incidents/form.html",
        {"form": form, "heading": "Unfall dokumentieren", "record_type": "accident"},
    )


@login_required
def incident_detail(request, pk):
    denied = guard(request)
    if denied:
        return denied
    incident=get_object_or_404(Incident.objects.prefetch_related("members", "supervisors", "guardians", "injured_members", "injured_supervisors"), pk=pk)
    if not incident_visible_to(request.user, incident): return HttpResponseForbidden("Diese Akte ist für dieses Benutzerkonto nicht mehr sichtbar.")
    return render(request,"incidents/detail.html",{"incident":incident,"can_edit_incident":incident_editable_by(request.user,incident),"can_archive_incident":is_leadership(request.user),"can_notify_command":is_leadership(request.user)})


@login_required
def incident_update(request, pk):
    denied = guard(request)
    if denied:
        return denied
    obj = get_object_or_404(Incident, pk=pk)
    if not incident_editable_by(request.user, obj): return HttpResponseForbidden("Betreuer können eigene Akten nur innerhalb von 24 Stunden bearbeiten.")
    form_class = AccidentReportForm if obj.record_type == Incident.RecordType.ACCIDENT else IncidentReportForm
    form = form_class(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Unfall wurde aktualisiert." if obj.record_type == Incident.RecordType.ACCIDENT else "Vorfall wurde aktualisiert.",
        )
        return redirect(obj)
    return render(
        request,
        "incidents/form.html",
        {
            "form": form,
            "heading": "Unfall bearbeiten" if obj.record_type == Incident.RecordType.ACCIDENT else "Vorfall bearbeiten",
            "incident": obj,
            "record_type": obj.record_type,
        },
    )


@login_required
@require_POST
def incident_archive(request, pk):
    if not is_leadership(request.user): return HttpResponseForbidden("Archivieren ist Jugendwarten und Administratoren vorbehalten.")
    obj = get_object_or_404(Incident, pk=pk)
    obj.archived = True
    obj.save(update_fields=("archived", "updated_at"))
    messages.success(request, "Dokumentation wurde archiviert.")
    return redirect("incidents:list")


@login_required
@require_POST
def notify_command(request, pk):
    if not is_leadership(request.user): return HttpResponseForbidden("Unfallmeldungen an die Wehrführung dürfen nur Jugendwarte oder Administratoren senden.")
    obj = get_object_or_404(Incident, pk=pk)
    if obj.record_type != Incident.RecordType.ACCIDENT:
        messages.error(request, "Eine Unfallmeldung ist nur bei einer Unfalldokumentation möglich.")
        return redirect(obj)
    recipients = [x.strip() for x in os.getenv("INCIDENT_COMMAND_EMAILS", "").split(",") if x.strip()]
    if not recipients:
        messages.error(request, "Keine Empfänger in INCIDENT_COMMAND_EMAILS konfiguriert.")
        return redirect(obj)
    body = (
        "Unfallmeldung Jugendfeuerwehr\n\n"
        f"Datum: {timezone.localtime(obj.occurred_at):%d.%m.%Y %H:%M}\n"
        f"Unfall: {obj.title}\n"
        f"Termin: {obj.activity or 'kein Termin'}\n\n"
        f"Dokumentation:\n{obj.documentation}\n\n"
        f"Verletzte Mitglieder: {', '.join(str(x) for x in obj.injured_members.all()) or '-'}\n"
        f"Verletzte Betreuer: {', '.join(str(x) for x in obj.injured_supervisors.all()) or '-'}\n"
        f"Sonstige verletzte Personen: {obj.injured_people or '-'}\n"
        f"Maßnahmen: {obj.first_aid or '-'}\n\n"
        f"Dokumentiert im JF-Manager durch: {obj.created_by or '-'}"
    )
    send_mail(
        f"Unfallmeldung Jugendfeuerwehr – {obj.occurred_at:%d.%m.%Y}",
        body,
        None,
        recipients,
        fail_silently=False,
    )
    obj.command_notification_sent_at = timezone.now()
    obj.command_notification_sent_by = request.user
    obj.save(update_fields=("command_notification_sent_at", "command_notification_sent_by", "updated_at"))
    messages.success(request, "Unfallmeldung wurde an die Wehrführung gesendet.")
    return redirect(obj)
