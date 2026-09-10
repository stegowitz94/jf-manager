from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render
from .models import AuditEvent
@login_required
def audit_list(request):
    if not (request.user.is_superuser or request.user.role=="admin"): return HttpResponseForbidden("Nur für Administratoren")
    return render(request,"audit/list.html",{"events":AuditEvent.objects.select_related("actor")[:500]})
