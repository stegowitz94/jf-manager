from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import AppSettings


FEDERAL_STATES = [
    ("", "Bitte auswählen"), ("Baden-Württemberg", "Baden-Württemberg"), ("Bayern", "Bayern"),
    ("Berlin", "Berlin"), ("Brandenburg", "Brandenburg"), ("Bremen", "Bremen"),
    ("Hamburg", "Hamburg"), ("Hessen", "Hessen"), ("Mecklenburg-Vorpommern", "Mecklenburg-Vorpommern"),
    ("Niedersachsen", "Niedersachsen"), ("Nordrhein-Westfalen", "Nordrhein-Westfalen"),
    ("Rheinland-Pfalz", "Rheinland-Pfalz"), ("Saarland", "Saarland"), ("Sachsen", "Sachsen"),
    ("Sachsen-Anhalt", "Sachsen-Anhalt"), ("Schleswig-Holstein", "Schleswig-Holstein"), ("Thüringen", "Thüringen"),
]


class OrganisationSetupForm(forms.ModelForm):
    federal_state = forms.ChoiceField(label="Bundesland", choices=FEDERAL_STATES, required=False)
    class Meta:
        model = AppSettings
        fields = ("organisation_name", "short_name", "fire_department_name", "federal_state", "street", "postal_code", "city", "contact_email", "website")


class AdminSetupForm(forms.Form):
    first_name = forms.CharField(label="Vorname", max_length=150)
    last_name = forms.CharField(label="Nachname", max_length=150)
    username = forms.CharField(label="Benutzername", max_length=150, initial="admin")
    email = forms.EmailField(label="E-Mail-Adresse")
    password1 = forms.CharField(label="Passwort", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Passwort wiederholen", widget=forms.PasswordInput)
    privacy_ack = forms.BooleanField(label="Hinweise zu Datenschutz und Betrieb zur Kenntnis genommen", required=True)

    def clean_username(self):
        value = self.cleaned_data["username"]
        if get_user_model().objects.filter(username__iexact=value).exists():
            raise forms.ValidationError("Dieser Benutzername ist bereits vergeben.")
        return value

    def clean(self):
        data = super().clean()
        p1, p2 = data.get("password1"), data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Die Passwörter stimmen nicht überein.")
        if p1:
            validate_password(p1)
        return data
