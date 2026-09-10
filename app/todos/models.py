from django.conf import settings
from django.db import models
from django.utils import timezone
from members.models import Member

class Todo(models.Model):
    class Category(models.TextChoices):
        TEAM='team','Teamintern'
        FAMILY='family','Mit Kind / Eltern klären'
    class TargetType(models.TextChoices):
        SINGLE='single','Ein Mitglied'
        MULTIPLE='multiple','Mehrere Mitglieder'
        ALL='all','Alle Mitglieder'
    title=models.CharField('Titel',max_length=200)
    description=models.TextField('Beschreibung',blank=True)
    category=models.CharField('Kategorie',max_length=20,choices=Category.choices,default=Category.TEAM)
    target_type=models.CharField('Gilt für',max_length=20,choices=TargetType.choices,default=TargetType.SINGLE)
    members=models.ManyToManyField(Member,blank=True,related_name='todos')
    deadline=models.DateField('Deadline')
    assigned_to=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name='assigned_todos',verbose_name='Zuständig')
    completed=models.BooleanField('Erledigt',default=False)
    completed_at=models.DateTimeField(null=True,blank=True)
    completed_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name='completed_todos')
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,on_delete=models.SET_NULL,related_name='created_todos')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=('completed','deadline','title')
    def __str__(self): return self.title
    @property
    def overdue(self): return not self.completed and self.deadline < timezone.localdate()

class TodoMemberStatus(models.Model):
    todo=models.ForeignKey(Todo,on_delete=models.CASCADE,related_name='member_statuses')
    member=models.ForeignKey(Member,on_delete=models.CASCADE,related_name='todo_statuses')
    completed=models.BooleanField(default=False)
    completed_at=models.DateTimeField(null=True,blank=True)
    completed_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name='completed_member_todos')
    note=models.CharField('Notiz',max_length=300,blank=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=('todo','member'),name='unique_todo_member_status')]
