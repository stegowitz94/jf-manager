from datetime import datetime, time
from calendar import monthrange
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count,Q
from django.http import HttpResponseBadRequest,JsonResponse
from django.shortcuts import get_object_or_404,redirect,render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import ActivityForm,ImportForm
from .importer import parse_divera
from .models import Activity,Attendance,SupervisorAttendance,ActivityTypeSetting
from .services import initialize_attendance,initialize_supervisor_attendance
from todos.models import TodoMemberStatus
from members.models import Member

@login_required
def activity_list(request):
    year=int(request.GET.get("year") or timezone.localdate().year); kind=request.GET.get("type","")
    activities=Activity.objects.filter(starts_at__year=year).annotate(present_count=Count("attendances",filter=Q(attendances__status=Attendance.Status.PRESENT)),excused_count=Count("attendances",filter=Q(attendances__status=Attendance.Status.EXCUSED)),unexcused_count=Count("attendances",filter=Q(attendances__status=Attendance.Status.UNEXCUSED)))
    if kind: activities=activities.filter(activity_type=kind)
    return render(request,"activities/activity_list.html",{"activities":activities,"year":year,"kind":kind,"years":range(timezone.localdate().year-3,timezone.localdate().year+3),"types":Activity.ActivityType.choices})

@login_required
def activity_calendar(request):
    today=timezone.localdate(); year=int(request.GET.get("year") or today.year); month=int(request.GET.get("month") or today.month)
    days=[]; by_day={}
    for a in Activity.objects.filter(starts_at__year=year,starts_at__month=month).order_by("starts_at"):
        by_day.setdefault(timezone.localtime(a.starts_at).day,[]).append(a)
    first=datetime(year,month,1).weekday(); total=monthrange(year,month)[1]
    days=[None]*first+[(d,by_day.get(d,[])) for d in range(1,total+1)]
    prev_month=12 if month==1 else month-1; prev_year=year-1 if month==1 else year
    next_month=1 if month==12 else month+1; next_year=year+1 if month==12 else year
    return render(request,"activities/activity_calendar.html",locals())

@login_required
def activity_create(request):
    now = timezone.localtime()
    initial = {}
    if request.method != "POST":
        setting = ActivityTypeSetting.objects.filter(activity_type=Activity.ActivityType.GROUP).first()
        start_time = setting.default_start_time if setting and setting.default_start_time else time(17, 15)
        end_time = setting.default_end_time if setting and setting.default_end_time else time(18, 45)
        initial = {
            "activity_type": Activity.ActivityType.GROUP,
            "starts_at": now.replace(hour=start_time.hour, minute=start_time.minute, second=0, microsecond=0),
            "ends_at": now.replace(hour=end_time.hour, minute=end_time.minute, second=0, microsecond=0),
        }
    form=ActivityForm(request.POST or None,initial=initial)
    if request.method=="POST" and form.is_valid():
        a=form.save(commit=False); a.created_by=request.user; a.save(); initialize_attendance(a,request.user); initialize_supervisor_attendance(a,request.user); messages.success(request,"Termin wurde angelegt."); return redirect("activities:attendance",pk=a.pk)
    return render(request,"activities/activity_form.html",{"form":form,"heading":"Neuer Termin"})

@login_required
def activity_update(request,pk):
    a=get_object_or_404(Activity,pk=pk); form=ActivityForm(request.POST or None,instance=a)
    if request.method=="POST" and form.is_valid(): form.save(); messages.success(request,"Termin wurde gespeichert."); return redirect("activities:attendance",pk=a.pk)
    return render(request,"activities/activity_form.html",{"form":form,"activity":a,"heading":"Termin bearbeiten"})

@login_required
def activity_delete(request,pk):
    a=get_object_or_404(Activity,pk=pk)
    if request.method=="POST": a.delete(); messages.success(request,"Termin wurde gelöscht."); return redirect("activities:list")
    return render(request,"activities/activity_confirm_delete.html",{"activity":a})

@login_required
def activity_import(request):
    form=ImportForm(request.POST or None,request.FILES or None)
    if request.method=="POST" and form.is_valid():
        try: rows=parse_divera(form.cleaned_data["file"].read())
        except Exception as exc: form.add_error("file",str(exc))
        else:
            request.session["activity_import"]={"rows":rows,"activity_type":form.cleaned_data["activity_type"]}; return render(request,"activities/import_preview.html",{"rows":rows,"valid_count":sum("error" not in r for r in rows)})
    return render(request,"activities/import_form.html",{"form":form})

@login_required
@require_POST
def activity_import_confirm(request):
    payload=request.session.pop("activity_import",None)
    if not payload: messages.error(request,"Keine Importvorschau vorhanden."); return redirect("activities:import")
    created=duplicates=errors=0
    with transaction.atomic():
        for row in payload["rows"]:
            if "error" in row: errors+=1; continue
            start=datetime.fromisoformat(row["starts_at"]); end=datetime.fromisoformat(row["ends_at"]) if row["ends_at"] else None
            if Activity.objects.filter(starts_at=start,ends_at=end,title=row["title"]).exists(): duplicates+=1; continue
            a=Activity.objects.create(title=row["title"],activity_type=payload["activity_type"],starts_at=start,ends_at=end,location=row["location"],description=row["description"],created_by=request.user,import_source=Activity.ImportSource.DIVERA,imported_at=timezone.now()); initialize_attendance(a,request.user); initialize_supervisor_attendance(a,request.user); created+=1
    messages.success(request,f"Import abgeschlossen: {created} neu, {duplicates} Duplikate, {errors} fehlerhaft."); return redirect("activities:list")

@login_required
def attendance(request,pk):
    activity=get_object_or_404(Activity,pk=pk)
    initialize_attendance(activity,request.user)
    initialize_supervisor_attendance(activity,request.user)
    rows=activity.attendances.select_related("member")
    supervisor_rows=activity.supervisor_attendances.select_related("supervisor")
    counts={s:rows.filter(status=s).count() for s in Attendance.Status.values}
    supervisor_counts={s:supervisor_rows.filter(status=s).count() for s in SupervisorAttendance.Status.values}
    from todos.models import Todo
    all_family_todos=Todo.objects.filter(category=Todo.Category.FAMILY,target_type=Todo.TargetType.ALL,completed=False)
    for row in rows:
        for todo in all_family_todos:
            TodoMemberStatus.objects.get_or_create(todo=todo,member=row.member)

    # RC2.1: To-Dos werden gesammelt unterhalb der Anwesenheitslisten dargestellt,
    # statt die einzelnen Mitgliedszeilen aufzublähen.
    open_statuses=(TodoMemberStatus.objects
        .select_related("todo","member")
        .filter(completed=False,todo__completed=False,todo__category=Todo.Category.FAMILY)
        .exclude(member__activity_status=Member.ActivityStatus.RESIGNED)
        .order_by("todo__deadline","todo__title","member__last_name","member__first_name"))
    todo_groups=[]
    by_todo={}
    for status in open_statuses:
        group=by_todo.get(status.todo_id)
        if group is None:
            group={"todo":status.todo,"statuses":[],"open_count":0}
            by_todo[status.todo_id]=group
            todo_groups.append(group)
        group["statuses"].append(status)
        group["open_count"]+=1

    return render(request,"activities/attendance.html",{
        "activity":activity,
        "rows":rows,
        "supervisor_rows":supervisor_rows,
        "counts":{"present":counts["present"],"excused":counts["excused"],"unexcused":counts["unexcused"]},
        "supervisor_counts":{"present":supervisor_counts["present"],"excused":supervisor_counts["excused"],"unexcused":supervisor_counts["unexcused"]},
        "status_choices":Attendance.Status.choices,
        "supervisor_status_choices":SupervisorAttendance.Status.choices,
        "todo_groups":todo_groups,
    })

@login_required
@require_POST
def attendance_update(request,pk,attendance_pk):
    activity=get_object_or_404(Activity,pk=pk); row=get_object_or_404(Attendance,pk=attendance_pk,activity=activity); status=request.POST.get("status")
    if status not in Attendance.Status.values:return HttpResponseBadRequest("Ungültiger Anwesenheitsstatus")
    row.status=status; row.source=Attendance.Source.MANUAL; row.updated_by=request.user; row.save(update_fields=("status","source","updated_by","updated_at"))
    return JsonResponse({"ok":True,"status":row.status,"scope":"member","counts":{s:activity.attendances.filter(status=s).count() for s in Attendance.Status.values}})

@login_required
@require_POST
def supervisor_attendance_update(request,pk,attendance_pk):
    activity=get_object_or_404(Activity,pk=pk)
    row=get_object_or_404(SupervisorAttendance,pk=attendance_pk,activity=activity)
    status=request.POST.get("status")
    if status not in SupervisorAttendance.Status.values:
        return HttpResponseBadRequest("Ungültiger Anwesenheitsstatus")
    row.status=status
    row.source=SupervisorAttendance.Source.MANUAL
    row.updated_by=request.user
    row.save(update_fields=("status","source","updated_by","updated_at"))
    return JsonResponse({
        "ok":True,
        "status":row.status,
        "scope":"supervisor",
        "counts":{s:activity.supervisor_attendances.filter(status=s).count() for s in SupervisorAttendance.Status.values},
    })


@login_required
@require_POST
def supervisor_attendance_bulk(request,pk):
    activity=get_object_or_404(Activity,pk=pk)
    status=request.POST.get("status")
    if status not in SupervisorAttendance.Status.values:
        return HttpResponseBadRequest("Ungültiger Anwesenheitsstatus")
    activity.supervisor_attendances.update(
        status=status,source=SupervisorAttendance.Source.MANUAL,updated_by=request.user
    )
    messages.success(request,"Alle Betreuer-Einträge wurden aktualisiert.")
    return redirect("activities:attendance",pk=pk)


@login_required
@require_POST
def attendance_bulk(request,pk):
    activity=get_object_or_404(Activity,pk=pk); status=request.POST.get("status")
    if status not in Attendance.Status.values:return HttpResponseBadRequest("Ungültiger Anwesenheitsstatus")
    activity.attendances.update(status=status,source=Attendance.Source.MANUAL,updated_by=request.user); messages.success(request,"Alle Einträge wurden aktualisiert."); return redirect("activities:attendance",pk=pk)

@login_required
@require_POST
def attendance_complete(request,pk):
    activity=get_object_or_404(Activity,pk=pk)
    present_ids=activity.attendances.filter(status=Attendance.Status.PRESENT).values_list("member_id",flat=True)
    open_points=TodoMemberStatus.objects.select_related("todo","member").filter(member_id__in=present_ids,completed=False,todo__completed=False,todo__category="family")
    if open_points.exists() and request.POST.get("confirm_open_todos") != "yes":
        return render(request,"activities/attendance_open_todos_confirm.html",{"activity":activity,"open_points":open_points})
    activity.attendance_completed=True; activity.save(update_fields=("attendance_completed","updated_at"))
    if activity.counts_for_attendance_statistics:
        try:
            from notifications.tasks import evaluate_activity_absences
            evaluate_activity_absences.delay(activity.pk)
        except Exception: pass
    messages.success(request,"Anwesenheitsliste wurde abgeschlossen."); return redirect("activities:attendance",pk=pk)


@login_required
def activity_type_defaults(request):
    activity_type = request.GET.get("type", "")
    if activity_type not in Activity.ActivityType.values:
        return JsonResponse({"start": None, "end": None})
    setting = ActivityTypeSetting.objects.filter(activity_type=activity_type).first()
    defaults = {
        Activity.ActivityType.GROUP: (time(17, 15), time(18, 45)),
        Activity.ActivityType.DRILL: (time(17, 15), time(18, 45)),
    }
    fallback_start, fallback_end = defaults.get(activity_type, (None, None))
    start = setting.default_start_time if setting else fallback_start
    end = setting.default_end_time if setting else fallback_end
    return JsonResponse({
        "start": start.strftime("%H:%M") if start else None,
        "end": end.strftime("%H:%M") if end else None,
    })
