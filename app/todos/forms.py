from django import forms
from members.models import Member
from .models import Todo
class TodoForm(forms.ModelForm):
    class Meta:
        model=Todo; fields=('title','description','category','target_type','members','deadline','assigned_to')
        widgets={'description':forms.Textarea(attrs={'rows':3}),'deadline':forms.DateInput(attrs={'type':'date'}),'members':forms.SelectMultiple(attrs={'class':'multi-person-source','data-person-picker':'member','data-placeholder':'Mitglieder suchen …'})}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['members'].queryset=Member.objects.exclude(activity_status=Member.ActivityStatus.RESIGNED).order_by('last_name','first_name')
    def clean(self):
        d=super().clean()
        if d.get('category')==Todo.Category.FAMILY and d.get('target_type') in (Todo.TargetType.SINGLE,Todo.TargetType.MULTIPLE) and not d.get('members'):
            self.add_error('members','Bitte mindestens ein Mitglied auswählen.')
        return d
