from django.db import migrations,models
class Migration(migrations.Migration):
 dependencies=[('incidents','0002_split_incident_accident'),('members','0005_memberbadge'),('supervisors','0002_supervisortraining')]
 operations=[migrations.AddField(model_name='incident',name='injured_members',field=models.ManyToManyField(blank=True,related_name='injury_incidents',to='members.member',verbose_name='Verletzte Mitglieder')),migrations.AddField(model_name='incident',name='injured_supervisors',field=models.ManyToManyField(blank=True,related_name='injury_incidents',to='supervisors.supervisor',verbose_name='Verletzte Betreuer'))]
