from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from core.image_utils import optimize_profile_image
from .models import Guardian, Leave, Member, MemberBadge
from .imports import IMPORT_FIELDS
from openpyxl.utils import get_column_letter


class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("format", "%Y-%m-%d")
        super().__init__(*args, **kwargs)


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = (
            "sequential_number", "first_name", "last_name", "gender", "entry_date", "jf_card_number",
            "activity_status", "birth_date", "street", "postal_code", "city", "phone", "mobile", "email",
            "profile_image", "photo_video_permission", "divera_permission",
            "school_or_employer", "vocational_training", "career_goal", "other_organizations",
            "health_notes", "swimming_status", "health_insurance",
        )
        widgets = {
            "entry_date": DateInput(),
            "birth_date": DateInput(),
            "profile_image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
            "other_organizations": forms.Textarea(attrs={"rows": 3}),
            "health_notes": forms.Textarea(attrs={"rows": 5}),
        }

    def clean_profile_image(self):
        image = self.cleaned_data.get("profile_image")
        if image and getattr(image, "size", 0) > 12 * 1024 * 1024:
            raise forms.ValidationError("Das Bild darf höchstens 12 MB groß sein.")
        if image and (hasattr(image, "temporary_file_path") or hasattr(image, "read")):
            if image != getattr(self.instance, "profile_image", None):
                return optimize_profile_image(image, "mitglied-profil")
        return image


class GuardianForm(forms.ModelForm):
    class Meta:
        model = Guardian
        fields = ("priority", "first_name", "last_name", "phone", "email")


class RequiredGuardianFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        active_forms = [
            form for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get("DELETE", False)
        ]
        if not active_forms:
            raise forms.ValidationError("Mindestens eine erziehungsberechtigte Person ist erforderlich.")
        if len(active_forms) > 2:
            raise forms.ValidationError("Es dürfen höchstens zwei erziehungsberechtigte Personen erfasst werden.")
        priorities = [form.cleaned_data.get("priority") for form in active_forms]
        if len(priorities) != len(set(priorities)):
            raise forms.ValidationError("Die Prioritäten der erziehungsberechtigten Personen müssen unterschiedlich sein.")


GuardianFormSet = inlineformset_factory(
    Member,
    Guardian,
    form=GuardianForm,
    formset=RequiredGuardianFormSet,
    extra=2,
    min_num=1,
    validate_min=True,
    max_num=2,
    validate_max=True,
    can_delete=True,
)


class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ("start_date", "planned_end_date", "status_after", "note")
        widgets = {"start_date": DateInput(), "planned_end_date": DateInput()}


class MemberImportUploadForm(forms.Form):
    file = forms.FileField(
        label="Excel-Datei",
        help_text="Unterstützt werden .xlsx-Dateien bis 10 MB.",
        widget=forms.ClearableFileInput(attrs={"accept": ".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}),
    )

    def clean_file(self):
        upload = self.cleaned_data["file"]
        if not upload.name.lower().endswith(".xlsx"):
            raise forms.ValidationError("Bitte eine Excel-Datei im Format .xlsx auswählen.")
        if upload.size > 10 * 1024 * 1024:
            raise forms.ValidationError("Die Excel-Datei darf höchstens 10 MB groß sein.")
        return upload


class MemberImportSheetForm(forms.Form):
    sheet_name = forms.ChoiceField(label="Tabellenblatt")
    header_row = forms.IntegerField(label="Kopfzeile", min_value=1, initial=1, help_text="Zeilennummer, in der die Spaltenüberschriften stehen.")

    def __init__(self, *args, sheet_names=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sheet_name"].choices = [(name, name) for name in (sheet_names or [])]


class MemberImportMappingForm(forms.Form):
    sheet_name = forms.CharField(widget=forms.HiddenInput())
    header_row = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, headers=None, suggestions=None, **kwargs):
        super().__init__(*args, **kwargs)
        headers = headers or []
        suggestions = suggestions or {}
        choices = [("", "Nicht importieren")] + [(str(index), f"{get_column_letter(index + 1)} – {label}") for index, label in enumerate(headers)]
        for field_name, label, required in IMPORT_FIELDS:
            self.fields[f"map_{field_name}"] = forms.ChoiceField(
                label=label + (" *" if required else ""),
                choices=choices,
                required=required,
                initial=str(suggestions[field_name]) if field_name in suggestions else "",
            )

    def clean(self):
        cleaned = super().clean()
        selected = {}
        for field_name, _label, required in IMPORT_FIELDS:
            raw = cleaned.get(f"map_{field_name}")
            if raw not in (None, ""):
                selected[field_name] = int(raw)
            elif required:
                self.add_error(f"map_{field_name}", "Dieses Pflichtfeld muss einer Excel-Spalte zugeordnet werden.")
        values = list(selected.values())
        if len(values) != len(set(values)):
            raise forms.ValidationError("Jede Excel-Spalte darf nur einem JF-Manager-Feld zugeordnet werden.")
        cleaned["mapping"] = selected
        return cleaned


class MemberBadgeForm(forms.ModelForm):
    class Meta:
        model = MemberBadge
        fields = ("badge_type", "custom_name", "awarded_on", "note")
        widgets = {"awarded_on": DateInput(), "note": forms.Textarea(attrs={"rows": 3})}
    def clean(self):
        data=super().clean()
        if data.get("badge_type") == MemberBadge.BadgeType.OTHER and not (data.get("custom_name") or "").strip():
            self.add_error("custom_name", "Bitte eine Bezeichnung für das sonstige Abzeichen angeben.")
        return data
