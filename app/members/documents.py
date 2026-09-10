from __future__ import annotations

from datetime import date
from html import escape
from io import BytesIO

from django.http import FileResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _value(value):
    return escape(str(value or "–"))


def _change_line(styles, lines=1):
    line = "_______________________________________________"
    return Paragraph("<br/>".join([line] * lines), styles["TableBody"])


def _member_story(member, styles, app_settings=None):
    guardians = list(member.guardians.all())
    header_title = Paragraph(f"<b>{escape(app_settings.organisation_name if app_settings else 'Jugendfeuerwehr')}</b><br/>Stammdaten-Prüfbogen", styles["TitleCompact"])
    if app_settings and app_settings.logo and app_settings.logo.path:
        try:
            logo = Image(app_settings.logo.path, width=24*mm, height=24*mm, kind="proportional")
            header = Table([[logo, header_title]], colWidths=[30*mm, 146*mm])
        except Exception:
            header = header_title
    else:
        header = header_title
    story = [
        header,
        Paragraph(f"erstellt am {date.today():%d.%m.%Y}", styles["Small"]),
        Spacer(1, 3 * mm),
        Paragraph(f"<b>{_value(member.first_name)} {_value(member.last_name)}</b>", styles["HeadingCompact"]),
        Paragraph(
            "Bitte prüfen Sie die nachfolgenden Angaben. Tragen Sie Änderungen ausschließlich in der grau hinterlegten rechten Spalte ein. Sind alle Angaben korrekt, genügt die Bestätigung am Ende.",
            styles["Intro"],
        ),
        Spacer(1, 2.5 * mm),
    ]

    rows = [[
        Paragraph("Gespeicherte Angabe", styles["TableHead"]),
        Paragraph("Änderung / Ergänzung", styles["TableHead"]),
    ]]
    fields = [
        ("Vorname", member.first_name),
        ("Nachname", member.last_name),
        ("Geschlecht", member.get_gender_display()),
        ("Geburtsdatum", member.birth_date.strftime("%d.%m.%Y") if member.birth_date else ""),
        ("Straße und Hausnummer", member.street),
        ("PLZ / Ort", f"{member.postal_code} {member.city}".strip()),
        ("Telefon", member.phone),
        ("Mobil", member.mobile),
        ("E-Mail", member.email),
    ]
    for label, value in fields:
        rows.append([
            Paragraph(f"<b>{escape(label)}</b><br/>{_value(value)}", styles["TableBody"]),
            _change_line(styles),
        ])

    table = Table(rows, colWidths=[86 * mm, 90 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#B42335")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (1, 1), (1, -1), colors.HexColor("#F0F1F3")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B7BDC5")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.extend([table, Spacer(1, 3 * mm), Paragraph("Erziehungsberechtigte", styles["HeadingCompact"])])

    guardian_tables = []
    for idx in range(2):
        guardian = guardians[idx] if idx < len(guardians) else None
        name = f"{guardian.first_name} {guardian.last_name}" if guardian else "–"
        phone = guardian.phone if guardian else "–"
        email = guardian.email if guardian else "–"
        g_rows = [
            [
                Paragraph(f"<b>Kontakt {idx + 1}</b>", styles["TableHeadDark"]),
                Paragraph("Änderung / Ergänzung", styles["TableHeadDark"]),
            ],
            [
                Paragraph(
                    f"<b>Name:</b> {_value(name)}<br/><b>Telefon:</b> {_value(phone)}<br/><b>E-Mail:</b> {_value(email)}",
                    styles["TableBody"],
                ),
                _change_line(styles, lines=3),
            ],
        ]
        gtable = Table(g_rows, colWidths=[86 * mm, 90 * mm])
        gtable.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B7BDC5")),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E3E6EA")),
            ("BACKGROUND", (1, 1), (1, -1), colors.HexColor("#F0F1F3")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        guardian_tables.extend([gtable, Spacer(1, 2 * mm)])
    story.append(KeepTogether(guardian_tables))

    consent_rows = [
        [Paragraph("Foto-/Videoeinwilligung", styles["TableBody"]), Paragraph("Ja" if member.photo_video_permission else "Nein", styles["TableBody"])],
        [Paragraph("DIVERA-Einwilligung", styles["TableBody"]), Paragraph("Ja" if member.divera_permission else "Nein", styles["TableBody"])],
    ]
    consent_table = Table(consent_rows, colWidths=[86 * mm, 90 * mm])
    consent_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B7BDC5")),
        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#F0F1F3")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    footer = [
        Paragraph("Einwilligungen", styles["HeadingCompact"]),
        consent_table,
        Spacer(1, 2.5 * mm),
        Paragraph("Änderungen bei den Einwilligungen / weitere Hinweise:", styles["BodyCompact"]),
        Table([[Paragraph("", styles["BodyCompact"])]], colWidths=[176 * mm], rowHeights=[14 * mm], style=TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B7BDC5")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0F1F3")),
        ])),
        Spacer(1, 2.5 * mm),
        Paragraph("☐ Alle angegebenen Daten sind weiterhin korrekt. &nbsp;&nbsp;&nbsp; ☐ Änderungen wurden eingetragen.", styles["BodyCompact"]),
        Spacer(1, 4 * mm),
        Paragraph("Ort, Datum: ________________________________", styles["BodyCompact"]),
        Spacer(1, 4 * mm),
        Paragraph("Unterschrift Mitglied / erziehungsberechtigte Person: ______________________________________________", styles["BodyCompact"]),
        Spacer(1, 2.5 * mm),
        Paragraph(
            "Bitte prüfen Sie alle Angaben sorgfältig. Änderungen werden nach Rückgabe des Prüfbogens durch die Jugendfeuerwehr in die Mitgliederverwaltung übernommen.",
            styles["Small"],
        ),
    ]
    story.append(KeepTogether(footer))
    return story


def create_member_check_sheets(members, filename="Stammdaten-Pruefboegen.pdf", inline=False):
    stream = BytesIO()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=7, leading=8.5, textColor=colors.HexColor("#666666")))
    styles.add(ParagraphStyle(name="Intro", parent=styles["BodyText"], fontSize=8, leading=10))
    styles.add(ParagraphStyle(name="BodyCompact", parent=styles["BodyText"], fontSize=8, leading=9.5))
    styles.add(ParagraphStyle(name="TitleCompact", parent=styles["Title"], fontSize=17, leading=19, spaceAfter=1))
    styles.add(ParagraphStyle(name="HeadingCompact", parent=styles["Heading2"], fontSize=11, leading=13, spaceBefore=1, spaceAfter=2))
    styles.add(ParagraphStyle(name="TableHead", parent=styles["BodyText"], fontSize=7.5, leading=9, fontName="Helvetica-Bold", textColor=colors.white))
    styles.add(ParagraphStyle(name="TableHeadDark", parent=styles["BodyText"], fontSize=7.5, leading=9, fontName="Helvetica-Bold", textColor=colors.HexColor("#222222")))
    styles.add(ParagraphStyle(name="TableBody", parent=styles["BodyText"], fontSize=7.5, leading=9))
    doc = SimpleDocTemplate(
        stream,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=9 * mm,
        bottomMargin=9 * mm,
    )
    from core.models import AppSettings
    app_settings = AppSettings.load()
    story = []
    members = list(members)
    for index, member in enumerate(members):
        story.extend(_member_story(member, styles, app_settings))
        if index < len(members) - 1:
            story.append(PageBreak())
    doc.build(story)
    stream.seek(0)
    return FileResponse(stream, as_attachment=not inline, filename=filename)
