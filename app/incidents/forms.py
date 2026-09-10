from django import forms

from members.models import Guardian, Member
from supervisors.models import Supervisor

from .models import Incident


class GuardianMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.first_name} {obj.last_name} · Elternteil von {obj.member.first_name} {obj.member.last_name}"


class PersonPickerMixin:
    """Stellt M2M-Personenfelder als suchbare Mehrfachauswahl für das Frontend bereit."""

    def _configure_person_fields(self):
        self.fields["members"].queryset = Member.objects.exclude(activity_status=Member.ActivityStatus.RESIGNED).order_by(
            "last_name", "first_name"
        )
        self.fields["supervisors"].queryset = Supervisor.objects.exclude(
            activity_status=Supervisor.ActivityStatus.LEFT
        ).order_by("last_name", "first_name")
        self.fields["guardians"] = GuardianMultipleChoiceField(
            queryset=Guardian.objects.select_related("member").exclude(
                member__activity_status=Member.ActivityStatus.RESIGNED
            ).order_by("last_name", "first_name"),
            required=False,
            label="Betroffene Erziehungsberechtigte",
            initial=self.instance.guardians.all() if getattr(self.instance, "pk", None) else None,
            widget=forms.SelectMultiple(
                attrs={
                    "class": "multi-person-source",
                    "data-person-picker": "guardian",
                    "data-placeholder": "Erziehungsberechtigte suchen …",
                }
            ),
        )
        self.fields["members"].widget.attrs.update(
            {
                "class": "multi-person-source",
                "data-person-picker": "member",
                "data-placeholder": "Mitglied suchen …",
            }
        )
        self.fields["supervisors"].widget.attrs.update(
            {
                "class": "multi-person-source",
                "data-person-picker": "supervisor",
                "data-placeholder": "Betreuer suchen …",
            }
        )

    def _configure_dates(self):
        self.fields["occurred_at"].input_formats = ["%Y-%m-%dT%H:%M"]
        if "guardians_informed_at" in self.fields:
            self.fields["guardians_informed_at"].input_formats = ["%Y-%m-%dT%H:%M"]


class IncidentReportForm(PersonPickerMixin, forms.ModelForm):
    class Meta:
        model = Incident
        fields = (
            "occurred_at",
            "activity",
            "kind",
            "title",
            "members",
            "supervisors",
            "guardians",
            "other_people",
            "witnesses",
            "documentation",
        )
        widgets = {
            "occurred_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "documentation": forms.Textarea(attrs={"rows": 8}),
            "witnesses": forms.Textarea(attrs={"rows": 3}),
            "other_people": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._configure_dates()
        self._configure_person_fields()

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.record_type = Incident.RecordType.INCIDENT
        if commit:
            obj.save()
            self.save_m2m()
        return obj


class AccidentReportForm(PersonPickerMixin, forms.ModelForm):
    class Meta:
        model = Incident
        fields = (
            "occurred_at",
            "activity",
            "title",
            "members",
            "supervisors",
            "guardians",
            "other_people",
            "witnesses",
            "documentation",
            "injured_members",
            "injured_supervisors",
            "injured_people",
            "injury_description",
            "first_aid",
            "further_treatment",
            "guardians_informed",
            "guardians_informed_at",
        )
        widgets = {
            "occurred_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "guardians_informed_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "documentation": forms.Textarea(attrs={"rows": 8}),
            "witnesses": forms.Textarea(attrs={"rows": 3}),
            "other_people": forms.Textarea(attrs={"rows": 3}),
            "injured_people": forms.Textarea(attrs={"rows": 2}),
            "injury_description": forms.Textarea(attrs={"rows": 4}),
            "first_aid": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._configure_dates()
        self._configure_person_fields()
        self.fields["injured_members"].queryset = self.fields["members"].queryset
        self.fields["injured_supervisors"].queryset = self.fields["supervisors"].queryset
        self.fields["injured_members"].widget.attrs.update({"class":"multi-person-source","data-person-picker":"member","data-placeholder":"Verletztes Mitglied suchen …"})
        self.fields["injured_supervisors"].widget.attrs.update({"class":"multi-person-source","data-person-picker":"supervisor","data-placeholder":"Verletzten Betreuer suchen …"})
        if not self.is_bound and not self.instance.pk:
            from django.utils import timezone
            self.initial.setdefault("guardians_informed_at", timezone.localtime().strftime("%Y-%m-%dT%H:%M"))

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.record_type = Incident.RecordType.ACCIDENT
        obj.kind = Incident.Kind.GENERAL
        if commit:
            obj.save()
            self.save_m2m()
        return obj
