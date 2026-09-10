from io import BytesIO
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404,redirect,render
from openpyxl import Workbook
from members.models import Member
from members.views import next_free_sequential_number
from .forms import WaitingListEntryForm
from .models import WaitingListEntry

@login_required
def entry_list(request):
    from django.core.paginator import Paginator
    from core.models import UserTablePreference
    pref,_=UserTablePreference.objects.get_or_create(user=request.user,table_key="waitinglist")
    if request.GET.get("reset") == "1":
        pref.filters={}; pref.save(update_fields=("filters",)); return redirect("waitinglist:list")
    has_filters=any(k in request.GET for k in ("q","status"))
    if not has_filters and pref.filters:
        from urllib.parse import urlencode
        params=pref.filters.copy(); params["page_size"]=request.GET.get("page_size") or pref.page_size
        return redirect(f"{request.path}?{urlencode(params)}")
    qs=WaitingListEntry.objects.all(); q=(request.GET.get("q") or "").strip(); status=(request.GET.get("status") or "").strip()
    if q: qs=qs.filter(Q(first_name__icontains=q)|Q(last_name__icontains=q)|Q(city__icontains=q)|Q(phone__icontains=q)|Q(email__icontains=q))
    if status: qs=qs.filter(status=status)
    if has_filters: pref.filters={"q":q,"status":status}; pref.save(update_fields=("filters",))
    try: page_size=min(100,max(10,int(request.GET.get("page_size") or pref.page_size or 25)))
    except Exception: page_size=25
    if page_size != pref.page_size: pref.page_size=page_size; pref.save(update_fields=("page_size",))
    page_obj=Paginator(qs,page_size).get_page(request.GET.get("page"))
    return render(request,"waitinglist/list.html",{"entries":page_obj.object_list,"page_obj":page_obj,"q":q,"status":status,"status_choices":WaitingListEntry.Status.choices,"table_pref":pref})
@login_required
def entry_detail(request,pk): return render(request,"waitinglist/detail.html",{"entry":get_object_or_404(WaitingListEntry,pk=pk)})
@login_required
def entry_create(request):
    form=WaitingListEntryForm(request.POST or None)
    if form.is_valid(): obj=form.save(); messages.success(request,"Wartelisteneintrag wurde angelegt."); return redirect(obj)
    return render(request,"waitinglist/form.html",{"form":form,"title":"Wartelisteneintrag anlegen"})
@login_required
def entry_update(request,pk):
    obj=get_object_or_404(WaitingListEntry,pk=pk); form=WaitingListEntryForm(request.POST or None,instance=obj)
    if form.is_valid(): form.save(); messages.success(request,"Wartelisteneintrag wurde gespeichert."); return redirect(obj)
    return render(request,"waitinglist/form.html",{"form":form,"entry":obj,"title":"Wartelisteneintrag bearbeiten"})
@login_required
def convert_to_member(request,pk):
    obj=get_object_or_404(WaitingListEntry,pk=pk)
    if request.method=="POST":
        if not obj.birth_date:
            messages.error(request,"Für die Übernahme muss zuerst ein Geburtsdatum hinterlegt werden."); return redirect(obj)
        member=Member.objects.create(sequential_number=next_free_sequential_number(),first_name=obj.first_name,last_name=obj.last_name,birth_date=obj.birth_date,street=obj.street,postal_code=obj.postal_code,city=obj.city,phone=obj.phone,email=obj.email,activity_status=Member.ActivityStatus.ACTIVE)
        obj.status=WaitingListEntry.Status.ADMITTED; obj.save(update_fields=["status","updated_at"]); messages.success(request,"Der Eintrag wurde als Mitglied übernommen. Bitte Erziehungsberechtigte ergänzen."); return redirect("members:update",pk=member.pk)
    return redirect(obj)
@login_required
def export_xlsx(request):
    wb=Workbook(); ws=wb.active; ws.title="Warteliste"; ws.append(["Vorname","Nachname","Geburtsdatum","Telefon","E-Mail","Straße","PLZ","Ort","Status","Eingetragen am","Bemerkung"])
    for x in WaitingListEntry.objects.all(): ws.append([x.first_name,x.last_name,x.birth_date,x.phone,x.email,x.street,x.postal_code,x.city,x.get_status_display(),x.created_at.replace(tzinfo=None),x.note])
    out=BytesIO(); wb.save(out); response=HttpResponse(out.getvalue(),content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"); response["Content-Disposition"]='attachment; filename="JF-Warteliste.xlsx"'; return response
