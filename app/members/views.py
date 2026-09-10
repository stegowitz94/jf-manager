from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from pathlib import Path
from uuid import uuid4
from django.http import HttpResponseForbidden
from accounts.permissions import can_view_members, can_manage_members, can_view_sensitive_health

from .documents import create_member_check_sheets
from .exports import export_members_pdf, export_members_xlsx
from .imports import (
    IMPORT_FIELDS,
    create_import_template,
    detect_columns,
    import_preview_rows, validate_edited_preview_rows,
    inspect_workbook,
    parse_member_workbook,
    read_headers,
)
from .forms import (
    GuardianFormSet,
    LeaveForm,
    MemberForm,
    MemberImportMappingForm,
    MemberImportSheetForm,
    MemberImportUploadForm,
    MemberBadgeForm,
)
from .models import Leave, Member, MemberBadge


def next_free_sequential_number():
    used = set(Member.objects.values_list("sequential_number", flat=True))
    candidate = 1
    while candidate in used:
        candidate += 1
    return candidate


def filtered_members(request):
    members = Member.objects.prefetch_related("guardians").all()
    query = (request.GET.get("q") or request.POST.get("q") or "").strip()
    status = (request.GET.get("status") or request.POST.get("status") or "").strip()
    gender = (request.GET.get("gender") or request.POST.get("gender") or "").strip()
    if query:
        members = members.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(jf_card_number__icontains=query)
            | Q(sequential_number__icontains=query)
        )
    if status:
        members = members.filter(activity_status=status)
    if gender:
        members = members.filter(gender=gender)
    return members, query, status


@login_required
def member_list(request):
    if not can_view_members(request.user): return HttpResponseForbidden("Keine Berechtigung für die Mitgliederübersicht.")
    from django.core.paginator import Paginator
    from core.models import UserTablePreference
    pref,_=UserTablePreference.objects.get_or_create(user=request.user,table_key="members")
    if request.GET.get("reset") == "1":
        pref.filters={}; pref.save(update_fields=("filters",)); return redirect("members:list")
    has_filters=any(k in request.GET for k in ("q","status","gender"))
    if not has_filters and pref.filters:
        params=pref.filters.copy(); params["page_size"]=request.GET.get("page_size") or pref.page_size
        from urllib.parse import urlencode
        return redirect(f"{request.path}?{urlencode(params)}")
    members, query, status = filtered_members(request)
    gender=(request.GET.get("gender") or "").strip()
    if has_filters:
        pref.filters={"q":query,"status":status,"gender":gender}; pref.save(update_fields=("filters",))
    try: page_size=min(100,max(10,int(request.GET.get("page_size") or pref.page_size or 25)))
    except Exception: page_size=25
    if page_size != pref.page_size: pref.page_size=page_size; pref.save(update_fields=("page_size",))
    page_obj=Paginator(members,page_size).get_page(request.GET.get("page"))
    return render(request, "members/member_list.html", {"members": page_obj.object_list, "page_obj":page_obj, "query": query, "status": status, "gender":gender, "table_pref":pref})


@login_required
def member_export(request):
    if not can_manage_members(request.user): return HttpResponseForbidden("Exporte sind Jugendwarten und Administratoren vorbehalten.")
    members, query, status = filtered_members(request)
    if request.method == "POST":
        selected_statuses = request.POST.getlist("statuses")
        if selected_statuses:
            members = members.filter(activity_status__in=selected_statuses)
        export_format = request.POST.get("format", "xlsx")
        export_type = request.POST.get("template", "compact")
        if export_format == "pdf":
            return export_members_pdf(members, export_type)
        return export_members_xlsx(members)
    return render(request, "members/member_export.html", {"query": query, "status": status, "status_choices": Member.ActivityStatus.choices})


@login_required
def member_detail(request, pk):
    if not can_view_members(request.user): return HttpResponseForbidden("Keine Berechtigung für Mitgliedsdaten.")
    member = get_object_or_404(Member.objects.prefetch_related("guardians", "status_history", "leaves", "badges"), pk=pk)
    attendances = member.attendances.select_related("activity").filter(activity__attendance_completed=True).exclude(activity__activity_type="group", activity__participation_mode="voluntary").order_by("-activity__starts_at")[:20]
    total = member.attendances.filter(activity__attendance_completed=True).exclude(activity__activity_type="group", activity__participation_mode="voluntary").count()
    present = member.attendances.filter(activity__attendance_completed=True, status="present").exclude(activity__activity_type="group", activity__participation_mode="voluntary").count()
    attendance_rate = round(present / total * 100, 1) if total else 0
    return render(request, "members/member_detail.html", {
        "member": member, "attendances": attendances, "attendance_total": total,
        "attendance_present": present, "attendance_rate": attendance_rate,
        "can_view_sensitive_health": can_view_sensitive_health(request.user),
        "can_manage_member": can_manage_members(request.user),
    })


@login_required
@transaction.atomic
def member_create(request):
    if not can_manage_members(request.user): return HttpResponseForbidden("Diese Funktion ist Jugendwarten und Administratoren vorbehalten.")
    member = Member()
    if request.method == "POST":
        form = MemberForm(request.POST, request.FILES, instance=member)
        guardian_formset = GuardianFormSet(request.POST, instance=member, prefix="guardians")
        if form.is_valid() and guardian_formset.is_valid():
            member = form.save()
            guardian_formset.instance = member
            guardian_formset.save()
            messages.success(request, "Das Mitglied wurde angelegt.")
            return redirect(member)
    else:
        form = MemberForm(instance=member, initial={"sequential_number": next_free_sequential_number()})
        guardian_formset = GuardianFormSet(instance=member, prefix="guardians")
    return render(request, "members/member_form.html", {"form": form, "guardian_formset": guardian_formset, "title": "Mitglied anlegen"})


@login_required
@transaction.atomic
def member_update(request, pk):
    if not can_manage_members(request.user): return HttpResponseForbidden("Diese Funktion ist Jugendwarten und Administratoren vorbehalten.")
    member = get_object_or_404(Member, pk=pk)
    old_image = member.profile_image.name if member.profile_image else None
    if request.method == "POST":
        form = MemberForm(request.POST, request.FILES, instance=member)
        guardian_formset = GuardianFormSet(request.POST, instance=member, prefix="guardians")
        if form.is_valid() and guardian_formset.is_valid():
            member = form.save()
            guardian_formset.save()
            if old_image and member.profile_image and old_image != member.profile_image.name:
                member.profile_image.storage.delete(old_image)
            messages.success(request, "Die Mitgliedsdaten wurden gespeichert.")
            return redirect(member)
    else:
        form = MemberForm(instance=member)
        guardian_formset = GuardianFormSet(instance=member, prefix="guardians")
    return render(request, "members/member_form.html", {"form": form, "guardian_formset": guardian_formset, "member": member, "title": "Mitglied bearbeiten"})


@login_required
def leave_create(request, member_pk):
    if not can_manage_members(request.user): return HttpResponseForbidden("Diese Funktion ist Jugendwarten und Administratoren vorbehalten.")
    member = get_object_or_404(Member, pk=member_pk)
    if request.method == "POST":
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.member = member
            leave.created_by = request.user
            leave.save()
            messages.success(request, "Die Beurlaubung wurde angelegt.")
            return redirect(member)
    else:
        form = LeaveForm()
    return render(request, "members/leave_form.html", {"form": form, "member": member})


@login_required
def leave_update(request, pk):
    if not can_manage_members(request.user): return HttpResponseForbidden("Diese Funktion ist Jugendwarten und Administratoren vorbehalten.")
    leave = get_object_or_404(Leave, pk=pk)
    if request.method == "POST":
        form = LeaveForm(request.POST, instance=leave)
        if form.is_valid():
            form.save()
            messages.success(request, "Die Beurlaubung wurde gespeichert.")
            return redirect(leave.member)
    else:
        form = LeaveForm(instance=leave)
    return render(request, "members/leave_form.html", {"form": form, "member": leave.member, "leave": leave})


@login_required
def member_check_sheet(request, pk):
    if not can_manage_members(request.user): return HttpResponseForbidden("Diese Funktion ist Jugendwarten und Administratoren vorbehalten.")
    member = get_object_or_404(Member.objects.prefetch_related("guardians"), pk=pk)
    return create_member_check_sheets([member], filename=f"{member.last_name}_{member.first_name}_Stammdaten-Pruefbogen.pdf", inline=request.GET.get("print") == "1")


@login_required
def member_check_sheets_bulk(request):
    if not can_manage_members(request.user): return HttpResponseForbidden("Diese Funktion ist Jugendwarten und Administratoren vorbehalten.")
    members, _, _ = filtered_members(request)
    selected = request.POST.getlist("selected") if request.method == "POST" else []
    if selected:
        members = members.filter(pk__in=selected)
    members = members.prefetch_related("guardians")
    if not members.exists():
        messages.warning(request, "Für die Auswahl wurden keine Mitglieder gefunden.")
        return redirect("members:list")
    return create_member_check_sheets(members, filename="JF-Stammdaten-Pruefboegen.pdf", inline=request.GET.get("print") == "1")


@login_required
def member_import_template(request):
    if not can_manage_members(request.user): return HttpResponseForbidden("Diese Funktion ist Jugendwarten und Administratoren vorbehalten.")
    response = HttpResponse(
        create_import_template(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="JF-Manager_Mitgliederimport.xlsx"'
    return response


@login_required
def member_import(request):
    if not can_manage_members(request.user): return HttpResponseForbidden("Diese Funktion ist Jugendwarten und Administratoren vorbehalten.")
    step = "upload"
    upload_form = MemberImportUploadForm()
    sheet_form = None
    mapping_form = None
    preview = None
    workbook_info = None
    headers = None
    sample_rows = None

    def cleanup_import_file():
        stored = request.session.pop("member_import_file", None)
        if stored:
            path = Path(stored)
            import_root = (Path(settings.MEDIA_ROOT) / "imports").resolve()
            try:
                if path.resolve().is_relative_to(import_root) and path.exists():
                    path.unlink()
            except (OSError, ValueError):
                pass
        request.session.pop("member_import_preview", None)

    if request.method == "POST" and "cancel" in request.POST:
        cleanup_import_file()
        return redirect("members:import")

    if request.method == "POST" and "upload" in request.POST:
        cleanup_import_file()
        upload_form = MemberImportUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            upload = upload_form.cleaned_data["file"]
            import_dir = Path(settings.MEDIA_ROOT) / "imports"
            import_dir.mkdir(parents=True, exist_ok=True)
            temp_path = import_dir / f"{request.user.pk}-{uuid4().hex}.xlsx"
            with temp_path.open("wb") as destination:
                for chunk in upload.chunks():
                    destination.write(chunk)
            request.session["member_import_file"] = str(temp_path)
            request.session["member_import_original_name"] = upload.name
            try:
                workbook_info = inspect_workbook(temp_path)
                request.session["member_import_sheet_names"] = [sheet["name"] for sheet in workbook_info["sheets"]]
                sheet_form = MemberImportSheetForm(sheet_names=request.session["member_import_sheet_names"])
                step = "sheet"
            except ValueError as exc:
                cleanup_import_file()
                upload_form.add_error("file", str(exc))

    elif request.method == "POST" and "choose_sheet" in request.POST:
        stored = request.session.get("member_import_file")
        if not stored or not Path(stored).exists():
            messages.error(request, "Die hochgeladene Datei ist nicht mehr verfügbar. Bitte erneut hochladen.")
            return redirect("members:import")
        sheet_names = request.session.get("member_import_sheet_names", [])
        sheet_form = MemberImportSheetForm(request.POST, sheet_names=sheet_names)
        if sheet_form.is_valid():
            sheet_name = sheet_form.cleaned_data["sheet_name"]
            header_row = sheet_form.cleaned_data["header_row"]
            try:
                headers, sample_rows = read_headers(stored, sheet_name, header_row)
                suggestions = detect_columns(headers)
                mapping_form = MemberImportMappingForm(
                    initial={"sheet_name": sheet_name, "header_row": header_row},
                    headers=headers,
                    suggestions=suggestions,
                )
                request.session["member_import_headers"] = headers
                step = "mapping"
            except ValueError as exc:
                sheet_form.add_error(None, str(exc))
                step = "sheet"
        else:
            step = "sheet"

    elif request.method == "POST" and "preview" in request.POST:
        stored = request.session.get("member_import_file")
        headers = request.session.get("member_import_headers", [])
        if not stored or not Path(stored).exists() or not headers:
            messages.error(request, "Die Importdatei oder Spaltenauswahl ist abgelaufen. Bitte erneut beginnen.")
            return redirect("members:import")
        mapping_form = MemberImportMappingForm(request.POST, headers=headers)
        if mapping_form.is_valid():
            try:
                preview = parse_member_workbook(
                    stored,
                    sheet_name=mapping_form.cleaned_data["sheet_name"],
                    header_row=mapping_form.cleaned_data["header_row"],
                    mapping=mapping_form.cleaned_data["mapping"],
                )
                request.session["member_import_preview"] = preview["rows"]
                request.session["member_import_mapping"] = mapping_form.cleaned_data["mapping"]
                step = "preview"
            except ValueError as exc:
                mapping_form.add_error(None, str(exc))
                step = "mapping"
        else:
            step = "mapping"

    elif request.method == "POST" and "confirm" in request.POST:
        rows = request.session.get("member_import_preview")
        if not rows:
            messages.error(request, "Die Importvorschau ist abgelaufen. Bitte die Datei erneut hochladen.")
            return redirect("members:import")
        edited_rows = validate_edited_preview_rows(request.POST, rows)
        selected_rows = [row for row in edited_rows if row.get("selected")]
        if not selected_rows:
            preview = {"rows": edited_rows, "total": len(edited_rows)}
            step = "preview"
            messages.error(request, "Bitte mindestens eine Zeile für den Import auswählen.")
        elif any(row.get("errors") for row in selected_rows):
            preview = {"rows": edited_rows, "total": len(edited_rows)}
            request.session["member_import_preview"] = edited_rows
            step = "preview"
            messages.error(request, "Einige ausgewählte Zeilen enthalten noch Fehler. Bitte korrigiere sie oder schließe sie aus.")
        else:
            result = import_preview_rows(edited_rows)
            cleanup_import_file()
            messages.success(
                request,
                f"Import abgeschlossen: {result['created']} angelegt, {result['skipped']} übersprungen, {result['failed']} fehlgeschlagen.",
            )
            return redirect("members:list")

    elif request.method == "GET" and request.session.get("member_import_file"):
        cleanup_import_file()

    return render(
        request,
        "members/member_import.html",
        {
            "step": step,
            "upload_form": upload_form,
            "sheet_form": sheet_form,
            "mapping_form": mapping_form,
            "preview": preview,
            "workbook_info": workbook_info,
            "headers": headers,
            "sample_rows": sample_rows,
            "import_fields": IMPORT_FIELDS,
            "original_name": request.session.get("member_import_original_name"),
        },
    )



@login_required
def badge_create(request, member_pk):
    if not can_manage_members(request.user): return HttpResponseForbidden("Abzeichen dürfen nur Jugendwarte oder Administratoren verwalten.")
    member=get_object_or_404(Member,pk=member_pk)
    form=MemberBadgeForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        badge=form.save(commit=False); badge.member=member; badge.created_by=request.user; badge.save()
        messages.success(request,"Abzeichen wurde gespeichert."); return redirect(member.get_absolute_url()+"#abzeichen")
    return render(request,"members/badge_form.html",{"form":form,"member":member,"heading":"Abzeichen hinzufügen"})

@login_required
def badge_update(request, pk):
    if not can_manage_members(request.user): return HttpResponseForbidden("Abzeichen dürfen nur Jugendwarte oder Administratoren verwalten.")
    badge=get_object_or_404(MemberBadge,pk=pk); form=MemberBadgeForm(request.POST or None,instance=badge)
    if request.method=="POST" and form.is_valid(): form.save(); messages.success(request,"Abzeichen wurde aktualisiert."); return redirect(badge.member.get_absolute_url()+"#abzeichen")
    return render(request,"members/badge_form.html",{"form":form,"member":badge.member,"badge":badge,"heading":"Abzeichen bearbeiten"})

@login_required
@require_POST
def badge_delete(request, pk):
    if not can_manage_members(request.user): return HttpResponseForbidden("Abzeichen dürfen nur Jugendwarte oder Administratoren verwalten.")
    badge=get_object_or_404(MemberBadge,pk=pk); member=badge.member; badge.delete(); messages.success(request,"Abzeichen wurde gelöscht."); return redirect(member.get_absolute_url()+"#abzeichen")
