from django import forms

from core.image_utils import optimize_profile_image
from .models import Supervisor, SupervisorTraining


class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("format", "%Y-%m-%d")
        super().__init__(*args, **kwargs)


class SupervisorForm(forms.ModelForm):
    class Meta:
        model = Supervisor
        fields = (
            "sequential_number", "first_name", "last_name", "birth_date", "entry_date",
            "activity_status", "phone", "mobile", "email", "functions", "profile_image",
        )
        widgets = {
            "birth_date": DateInput(),
            "entry_date": DateInput(),
            "functions": forms.CheckboxSelectMultiple(),
            "profile_image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def clean_profile_image(self):
        image = self.cleaned_data.get("profile_image")
        if image and getattr(image, "size", 0) > 12 * 1024 * 1024:
            raise forms.ValidationError("Das Bild darf höchstens 12 MB groß sein.")
        if image and hasattr(image, "read") and image != getattr(self.instance, "profile_image", None):
            return optimize_profile_image(image, "betreuer-profil")
        return image


class SupervisorTrainingForm(forms.ModelForm):
    class Meta:
        model=SupervisorTraining
        fields=("title","category","provider","completed_on","valid_until","duration_units","certificate","note")
        widgets={"completed_on":DateInput(),"valid_until":DateInput(),"note":forms.Textarea(attrs={"rows":3}),"certificate":forms.ClearableFileInput(attrs={"accept":"application/pdf,image/*"})}
