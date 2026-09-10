from datetime import date, timedelta
import calendar
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from activities.models import Activity,Attendance
from core.models import AppSettings
from members.models import Member,Leave
from supervisors.models import Supervisor
from .models import NotificationLog, UserNotificationPreference
from .push import send_push

EVENT_FIELDS={"birthday":"birthdays","unexcused":"absences","excused":"absences","leave":"leave_end","activity":"upcoming_activity","scouting":"scouting"}

def eligible_users(kind):
    field=EVENT_FIELDS.get(kind)
    users=get_user_model().objects.filter(is_active=True)
    result=[]
    for user in users:
        if not (user.is_superuser or user.role in ("admin","youth_warden","deputy_youth_warden")): continue
        pref,_=UserNotificationPreference.objects.get_or_create(user=user)
        if field and not getattr(pref,field): continue
        result.append((user,pref))
    return result

def dispatch_once(key,kind,subject,body,url="/"):
    if NotificationLog.objects.filter(event_key=key).exists(): return False
    cfg=AppSettings.load(); users=eligible_users(kind)
    emails=set(cfg.recipient_list())
    for user,pref in users:
        if pref.email_enabled and user.email: emails.add(user.email)
    errors=[]; sent_any=False
    if emails:
        try: send_mail(subject,body,settings.DEFAULT_FROM_EMAIL,sorted(emails),fail_silently=False); sent_any=True
        except Exception as exc: errors.append(f"E-Mail: {exc}")
    push_count=0
    for user,pref in users:
        if not (pref.push_enabled and getattr(pref,EVENT_FIELDS.get(kind,"birthdays"),True)): continue
        for sub in list(user.push_subscriptions.all()):
            ok,error=send_push(sub,subject,body,url)
            if ok: push_count+=1; sent_any=True
            elif error: errors.append(f"Push {user}: {error}")
    NotificationLog.objects.create(event_key=key,notification_type=kind,subject=subject,recipients=", ".join(sorted(emails))+((f" · {push_count} Push" if push_count else "")),status="sent" if sent_any else "failed",error="\n".join(errors[:10]))
    return sent_any

@shared_task
def daily_notifications():
    today=timezone.localdate(); cfg=AppSettings.load()
    if cfg.birthday_notifications:
        people=[]
        for obj,label in ((Member,"Mitglied"),(Supervisor,"Betreuer")):
            for person in obj.objects.filter(birth_date__month=today.month,birth_date__day=today.day): people.append(f"{person.first_name} {person.last_name} ({label})")
        if people: dispatch_once(f"birthday:{today}","birthday",f"Geburtstage am {today:%d.%m.%Y}","Heute haben Geburtstag:\n- "+"\n- ".join(people),"/")
    if cfg.leave_notifications:
        target=today+timedelta(days=cfg.leave_notice_days)
        for leave in Leave.objects.filter(planned_end_date=target): dispatch_once(f"leave:{leave.pk}:{target}","leave",f"Beurlaubung endet: {leave.member}",f"Die Beurlaubung von {leave.member.first_name} {leave.member.last_name} endet am {target:%d.%m.%Y}.",f"/mitglieder/{leave.member_id}/")
    def subtract_months(value, months):
        total=value.year*12+value.month-1-months
        year,month0=divmod(total,12); month=month0+1
        return date(year,month,min(value.day,calendar.monthrange(year,month)[1]))
    scouting_target=today+timedelta(days=cfg.scouting_reminder_days)
    for member in Member.objects.filter(activity_status__in=(Member.ActivityStatus.ACTIVE,Member.ActivityStatus.TRANSITION)):
        try:
            sixteenth=member.birth_date.replace(year=member.birth_date.year+cfg.scouting_age_years)
        except ValueError:
            sixteenth=member.birth_date.replace(year=member.birth_date.year+cfg.scouting_age_years,day=28)
        eligible=subtract_months(sixteenth,cfg.scouting_lead_months)
        if eligible==scouting_target:
            dispatch_once(f"scouting:{member.pk}:{eligible}","scouting",f"Schnupperdienst bald möglich: {member}",f"{member.first_name} {member.last_name} darf ab {eligible:%d.%m.%Y} an Schnupperübungen der aktiven Abteilung teilnehmen.",f"/mitglieder/{member.pk}/")
    tomorrow=today+timedelta(days=1)
    for activity in Activity.objects.filter(starts_at__date=tomorrow).order_by("starts_at"):
        dispatch_once(f"activity:{activity.pk}:{tomorrow}","activity",f"Termin morgen: {activity.title}",f"{activity.title} beginnt morgen um {activity.starts_at:%H:%M} Uhr.",f"/termine/{activity.pk}/anwesenheit/")

@shared_task
def evaluate_activity_absences(activity_id):
    cfg=AppSettings.load()
    if not cfg.absence_notifications:return
    activity=Activity.objects.filter(pk=activity_id).first()
    if not activity or not activity.counts_for_attendance_statistics:return
    relevant=Activity.objects.filter(activity_type__in=(Activity.ActivityType.GROUP,Activity.ActivityType.DRILL),attendance_completed=True,starts_at__lte=activity.starts_at).exclude(activity_type=Activity.ActivityType.GROUP,participation_mode=Activity.ParticipationMode.VOLUNTARY).order_by("-starts_at")
    for member in Member.objects.exclude(activity_status=Member.ActivityStatus.RESIGNED):
        recent=list(Attendance.objects.filter(member=member,activity__in=relevant).select_related("activity").order_by("-activity__starts_at")[:max(cfg.unexcused_threshold,cfg.excused_threshold)])
        unexc=0
        for row in recent:
            if row.status==Attendance.Status.UNEXCUSED: unexc+=1
            else: break
        if unexc==cfg.unexcused_threshold: dispatch_once(f"unexcused:{member.pk}:{activity.pk}","unexcused",f"{unexc} unentschuldigte Fehltermine: {member}",f"{member.first_name} {member.last_name} hat bei {unexc} Terminen in Folge unentschuldigt gefehlt.",f"/mitglieder/{member.pk}/")
        exc=0
        for row in recent:
            if row.status==Attendance.Status.EXCUSED and row.source!=Attendance.Source.LEAVE: exc+=1
            else: break
        if exc==cfg.excused_threshold: dispatch_once(f"excused:{member.pk}:{activity.pk}","excused",f"{exc} entschuldigte Fehltermine: {member}",f"{member.first_name} {member.last_name} hat bei {exc} Terminen in Folge entschuldigt gefehlt.",f"/mitglieder/{member.pk}/")
