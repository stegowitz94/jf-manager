from io import BytesIO
from datetime import date
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
from django.shortcuts import render
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from activities.models import Activity,Attendance
from core.models import AppSettings
from members.models import Member
from supervisors.models import Supervisor
from waitinglist.models import WaitingListEntry

@login_required
def center(request): return render(request,"documents/center.html")
def _xlsx(filename,title,headers,rows):
    wb=Workbook(); ws=wb.active; ws.title=title; ws.append(headers)
    for row in rows: ws.append(row)
    ws.freeze_panes="A2"; ws.auto_filter.ref=ws.dimensions
    out=BytesIO(); wb.save(out); r=HttpResponse(out.getvalue(),content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"); r["Content-Disposition"]=f'attachment; filename="{filename}"'; return r
@login_required
def supervisors_export(request): return _xlsx("JF-Betreuer.xlsx","Betreuer",["Vorname","Nachname","Status","Funktionen","Telefon","Mobil","E-Mail"],([x.first_name,x.last_name,x.get_activity_status_display(),", ".join(x.functions.values_list("name",flat=True)),x.phone,x.mobile,x.email] for x in Supervisor.objects.prefetch_related("functions")))
@login_required
def activities_export(request): return _xlsx("JF-Termine.xlsx","Termine",["Beginn","Ende","Thema","Terminart","Ort","Anwesenheit abgeschlossen"],([x.starts_at.replace(tzinfo=None),x.ends_at.replace(tzinfo=None) if x.ends_at else None,x.title,x.get_activity_type_display(),x.location,"Ja" if x.attendance_completed else "Nein"] for x in Activity.objects.all()))
@login_required
def attendance_export(request): return _xlsx("JF-Anwesenheiten.xlsx","Anwesenheiten",["Termin","Datum","Mitglied","Status"],([x.activity.title,x.activity.starts_at.replace(tzinfo=None),str(x.member),x.get_status_display()] for x in Attendance.objects.select_related("activity","member")))

def _pdf_response(filename,title,headers,rows,landscape_mode=False):
    settings_obj=AppSettings.load(); out=BytesIO(); styles=getSampleStyleSheet(); pagesize=landscape(A4) if landscape_mode else A4
    doc=SimpleDocTemplate(out,pagesize=pagesize,leftMargin=12*mm,rightMargin=12*mm,topMargin=12*mm,bottomMargin=12*mm)
    story=[]
    if settings_obj.logo:
        try: story.append(Image(settings_obj.logo.path,width=22*mm,height=22*mm,kind="proportional"))
        except Exception: pass
    story += [Paragraph(settings_obj.organisation_name,styles["Heading2"]),Paragraph(title,styles["Title"]),Spacer(1,5*mm)]
    data=[[Paragraph(f"<b>{h}</b>",styles["BodyText"]) for h in headers]]+[[Paragraph(str(v or "–"),styles["BodyText"]) for v in row] for row in rows]
    widths=[(pagesize[0]-24*mm)/len(headers)]*len(headers); table=Table(data,colWidths=widths,repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#B42335")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.35,colors.HexColor("#B7BDC5")),("VALIGN",(0,0),(-1,-1),"TOP"),("FONTSIZE",(0,0),(-1,-1),8),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F3F4F6")])]))
    story.append(table); doc.build(story); out.seek(0); return FileResponse(out,filename=filename,as_attachment=True)

@login_required
def contact_pdf(request):
    rows=[]
    for m in Member.objects.exclude(activity_status=Member.ActivityStatus.RESIGNED).prefetch_related("guardians"):
        guardians="; ".join(f"{g.first_name} {g.last_name}: {g.phone or g.email}" for g in m.guardians.all())
        rows.append([f"{m.first_name} {m.last_name}",m.mobile or m.phone,m.email,guardians])
    return _pdf_response("JF-Kontaktliste.pdf","Kontaktliste",["Mitglied","Telefon","E-Mail","Erziehungsberechtigte"],rows,True)

@login_required
def birthdays_pdf(request):
    members=Member.objects.exclude(activity_status=Member.ActivityStatus.RESIGNED).order_by("birth_date__month","birth_date__day")
    rows=[[m.birth_date.strftime("%d.%m."),f"{m.first_name} {m.last_name}",date.today().year-m.birth_date.year] for m in members if m.birth_date]
    return _pdf_response("JF-Geburtstagsliste.pdf","Geburtstagsliste",["Datum","Name","Alter im laufenden Jahr"],rows)

@login_required
def waiting_pdf(request):
    rows=[[f"{w.first_name} {w.last_name}",w.phone,w.email,w.city,w.get_status_display()] for w in WaitingListEntry.objects.all()]
    return _pdf_response("JF-Warteliste.pdf","Warteliste",["Name","Telefon","E-Mail","Ort","Status"],rows,True)
