from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404,redirect,render
from django.utils import timezone
from django.views.decorators.http import require_POST
from members.models import Member
from .forms import TodoForm
from .models import Todo,TodoMemberStatus

def _sync(todo):
    if todo.category != Todo.Category.FAMILY: return
    qs=Member.objects.exclude(activity_status=Member.ActivityStatus.RESIGNED)
    if todo.target_type != Todo.TargetType.ALL: qs=todo.members.all()
    ids=list(qs.values_list('pk',flat=True))
    for mid in ids: TodoMemberStatus.objects.get_or_create(todo=todo,member_id=mid)
    todo.member_statuses.exclude(member_id__in=ids).delete()

@login_required
def todo_list(request):
    qs=Todo.objects.select_related('assigned_to').prefetch_related('members','member_statuses').all()
    return render(request,'todos/list.html',{'todos':qs})
@login_required
def todo_create(request):
    form=TodoForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        obj=form.save(commit=False); obj.created_by=request.user; obj.save(); form.save_m2m(); _sync(obj); messages.success(request,'To-Do wurde angelegt.'); return redirect('todos:list')
    return render(request,'todos/form.html',{'form':form,'heading':'Neues To-Do'})
@login_required
def todo_update(request,pk):
    obj=get_object_or_404(Todo,pk=pk); form=TodoForm(request.POST or None,instance=obj)
    if request.method=='POST' and form.is_valid(): form.save(); _sync(obj); messages.success(request,'To-Do wurde gespeichert.'); return redirect('todos:list')
    return render(request,'todos/form.html',{'form':form,'heading':'To-Do bearbeiten','todo':obj})
@login_required
@require_POST
def todo_complete(request,pk):
    obj=get_object_or_404(Todo,pk=pk); obj.completed=True; obj.completed_at=timezone.now(); obj.completed_by=request.user; obj.save(update_fields=('completed','completed_at','completed_by','updated_at')); messages.success(request,'To-Do erledigt.'); return redirect('todos:list')
@login_required
@require_POST
def member_complete(request,pk,status_pk):
    obj=get_object_or_404(Todo,pk=pk); status=get_object_or_404(TodoMemberStatus,pk=status_pk,todo=obj); status.completed=True; status.completed_at=timezone.now(); status.completed_by=request.user; status.save(update_fields=('completed','completed_at','completed_by')); return redirect(request.POST.get('next') or 'todos:list')

@login_required
@require_POST
def complete_present_members(request,pk,activity_pk):
    """Markiert einen Familien-To-Do-Punkt für alle aktuell anwesenden, betroffenen Mitglieder als erledigt."""
    from activities.models import Activity, Attendance
    obj=get_object_or_404(Todo,pk=pk,category=Todo.Category.FAMILY)
    activity=get_object_or_404(Activity,pk=activity_pk)
    present_ids=activity.attendances.filter(status=Attendance.Status.PRESENT).values_list('member_id',flat=True)
    statuses=obj.member_statuses.filter(member_id__in=present_ids,completed=False)
    now=timezone.now()
    count=statuses.update(completed=True,completed_at=now,completed_by=request.user)
    messages.success(request,f'{count} To-Do-Zuordnungen wurden für anwesende Mitglieder erledigt.')
    return redirect('activities:attendance',pk=activity.pk)
