from django import forms
from .models import WaitingListEntry
class DateInput(forms.DateInput): input_type="date"
class WaitingListEntryForm(forms.ModelForm):
    class Meta:
        model=WaitingListEntry
        fields=("first_name","last_name","birth_date","phone","email","street","postal_code","city","desired_entry_date","status","note")
        widgets={"birth_date":DateInput(format="%Y-%m-%d"),"desired_entry_date":DateInput(format="%Y-%m-%d"),"note":forms.Textarea(attrs={"rows":4})}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for n in ("birth_date","desired_entry_date"): self.fields[n].input_formats=["%Y-%m-%d"]
