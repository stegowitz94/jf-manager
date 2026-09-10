from django import forms
from .models import Activity

class ActivityForm(forms.ModelForm):
    class Meta:
        model=Activity
        fields=("title","activity_type","participation_mode","starts_at","ends_at","location","description")
        widgets={"starts_at":forms.DateTimeInput(attrs={"type":"datetime-local"},format="%Y-%m-%dT%H:%M"),"ends_at":forms.DateTimeInput(attrs={"type":"datetime-local"},format="%Y-%m-%dT%H:%M"),"description":forms.Textarea(attrs={"rows":3})}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["activity_type"].widget.attrs["data-activity-type"] = "true"
        self.fields["starts_at"].widget.attrs["data-starts-at"] = "true"
        self.fields["ends_at"].widget.attrs["data-ends-at"] = "true"
        self.fields["starts_at"].input_formats=["%Y-%m-%dT%H:%M"]
        self.fields["ends_at"].input_formats=["%Y-%m-%dT%H:%M"]

class ImportForm(forms.Form):
    file=forms.FileField(label="DIVERA-Excel-Datei",help_text="Unterstützt .xlsx-Dateien mit Begin, Ende, Thema, Text und Ort.")
    activity_type=forms.ChoiceField(label="Terminart",choices=Activity.ActivityType.choices,initial=Activity.ActivityType.GROUP)
