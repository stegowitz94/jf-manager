from collections import defaultdict
from datetime import date
from django.contrib.auth.decorators import login_required
from django.db.models import Count,Q
from django.shortcuts import get_object_or_404,render
from django.utils import timezone
from activities.models import Activity,Attendance
from members.models import Member

RELEVANT=(Activity.ActivityType.GROUP,Activity.ActivityType.DRILL)

def _pct(present,total): return round((present/total)*100,1) if total else 0

@login_required
def overview(request):
    year=int(request.GET.get("year") or timezone.localdate().year)
    qs=Attendance.objects.filter(activity__starts_at__year=year,activity__activity_type__in=RELEVANT,activity__attendance_completed=True).exclude(activity__activity_type=Activity.ActivityType.GROUP, activity__participation_mode=Activity.ParticipationMode.VOLUNTARY)
    totals=qs.aggregate(total=Count("id"),present=Count("id",filter=Q(status=Attendance.Status.PRESENT)),excused=Count("id",filter=Q(status=Attendance.Status.EXCUSED)),unexcused=Count("id",filter=Q(status=Attendance.Status.UNEXCUSED)))
    monthly=[]
    for month in range(1,13):
        m=qs.filter(activity__starts_at__month=month); total=m.count(); present=m.filter(status=Attendance.Status.PRESENT).count(); monthly.append({"month":month,"total":total,"present":present,"rate":_pct(present,total)})
    members=[]
    for m in Member.objects.exclude(activity_status=Member.ActivityStatus.RESIGNED):
        a=qs.filter(member=m); total=a.count(); present=a.filter(status=Attendance.Status.PRESENT).count(); members.append({"member":m,"total":total,"present":present,"excused":a.filter(status=Attendance.Status.EXCUSED).count(),"unexcused":a.filter(status=Attendance.Status.UNEXCUSED).count(),"rate":_pct(present,total)})
    members.sort(key=lambda x:(x["rate"],x["member"].last_name))
    today=timezone.localdate()
    age_groups=[{"label":"unter 10","count":0},{"label":"10–11","count":0},{"label":"12–13","count":0},{"label":"14–15","count":0},{"label":"16–17","count":0},{"label":"18+","count":0}]
    current_members=Member.objects.exclude(activity_status=Member.ActivityStatus.RESIGNED)
    for person in current_members:
        age=today.year-person.birth_date.year-((today.month,today.day)<(person.birth_date.month,person.birth_date.day))
        index=0 if age<10 else 1 if age<12 else 2 if age<14 else 3 if age<16 else 4 if age<18 else 5
        age_groups[index]["count"]+=1
    max_age=max([g["count"] for g in age_groups] or [1]) or 1
    for g in age_groups: g["percent"]=round(g["count"]/max_age*100,1)
    entry_years=[]
    for y in range(today.year-5,today.year+1):
        entry_years.append({"year":y,"count":Member.objects.filter(entry_date__year=y).count()})
    max_entries=max([x["count"] for x in entry_years] or [1]) or 1
    for x in entry_years: x["percent"]=round(x["count"]/max_entries*100,1)
    return render(request,"statistics/overview.html",{"year":year,"years":range(timezone.localdate().year-3,timezone.localdate().year+2),"totals":totals,"rate":_pct(totals["present"],totals["total"]),"monthly":monthly,"members":members,"age_groups":age_groups,"entry_years":entry_years})

@login_required
def member_detail(request,pk):
    member=get_object_or_404(Member,pk=pk); year=int(request.GET.get("year") or timezone.localdate().year)
    qs=member.attendances.filter(activity__starts_at__year=year,activity__activity_type__in=RELEVANT,activity__attendance_completed=True).exclude(activity__activity_type=Activity.ActivityType.GROUP, activity__participation_mode=Activity.ParticipationMode.VOLUNTARY).select_related("activity")
    total=qs.count(); present=qs.filter(status=Attendance.Status.PRESENT).count(); excused=qs.filter(status=Attendance.Status.EXCUSED).count(); unexcused=qs.filter(status=Attendance.Status.UNEXCUSED).count()
    return render(request,"statistics/member_detail.html",{"member":member,"year":year,"rows":qs.order_by("-activity__starts_at"),"total":total,"present":present,"excused":excused,"unexcused":unexcused,"rate":_pct(present,total)})
