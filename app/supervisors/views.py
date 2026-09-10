from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from accounts.permissions import is_leadership
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from .forms import SupervisorForm, SupervisorTrainingForm
from .models import Supervisor, SupervisorTraining



class LeadershipRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not is_leadership(request.user): return HttpResponseForbidden("Die Betreuerverwaltung ist Jugendwarten und Administratoren vorbehalten.")
        return super().dispatch(request,*args,**kwargs)

class SupervisorListView(LeadershipRequiredMixin, LoginRequiredMixin, ListView):
    model = Supervisor
    template_name = "supervisors/supervisor_list.html"
    context_object_name = "supervisors"
    paginate_by = 30

    def get_paginate_by(self, queryset):
        from core.models import UserTablePreference
        pref,_=UserTablePreference.objects.get_or_create(user=self.request.user,table_key="supervisors")
        try: value=min(100,max(10,int(self.request.GET.get("page_size") or pref.page_size or 30)))
        except Exception: value=30
        if value != pref.page_size: pref.page_size=value; pref.save(update_fields=("page_size",))
        return value

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related("functions")
        query = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "").strip()
        if query:
            qs = qs.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query))
        if status:
            qs = qs.filter(activity_status=status)
        return qs

    def get_context_data(self, **kwargs):
        from core.models import UserTablePreference
        ctx=super().get_context_data(**kwargs)
        ctx["table_pref"],_=UserTablePreference.objects.get_or_create(user=self.request.user,table_key="supervisors")
        return ctx


class SupervisorDetailView(LeadershipRequiredMixin, LoginRequiredMixin, DetailView):
    model = Supervisor
    template_name = "supervisors/supervisor_detail.html"


class SupervisorCreateView(LeadershipRequiredMixin, LoginRequiredMixin, CreateView):
    model = Supervisor
    form_class = SupervisorForm
    template_name = "supervisors/supervisor_form.html"


class SupervisorUpdateView(LeadershipRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Supervisor
    form_class = SupervisorForm
    template_name = "supervisors/supervisor_form.html"

    def form_valid(self, form):
        old_image = Supervisor.objects.filter(pk=self.object.pk).values_list("profile_image", flat=True).first()
        response = super().form_valid(form)
        new_image = self.object.profile_image.name if self.object.profile_image else None
        if old_image and old_image != new_image:
            self.object.profile_image.storage.delete(old_image)
        return response


@login_required
def training_create(request,pk):
    if not is_leadership(request.user): return HttpResponseForbidden("Keine Berechtigung.")
    supervisor=get_object_or_404(Supervisor,pk=pk); form=SupervisorTrainingForm(request.POST or None,request.FILES or None)
    if request.method=="POST" and form.is_valid(): obj=form.save(commit=False); obj.supervisor=supervisor; obj.save(); messages.success(request,"Fortbildung wurde gespeichert."); return redirect(supervisor)
    return render(request,"supervisors/training_form.html",{"form":form,"supervisor":supervisor,"heading":"Fortbildung hinzufügen"})
@login_required
def training_update(request,pk,training_pk):
    if not is_leadership(request.user): return HttpResponseForbidden("Keine Berechtigung.")
    supervisor=get_object_or_404(Supervisor,pk=pk); obj=get_object_or_404(SupervisorTraining,pk=training_pk,supervisor=supervisor); form=SupervisorTrainingForm(request.POST or None,request.FILES or None,instance=obj)
    if request.method=="POST" and form.is_valid(): form.save(); messages.success(request,"Fortbildung wurde aktualisiert."); return redirect(supervisor)
    return render(request,"supervisors/training_form.html",{"form":form,"supervisor":supervisor,"heading":"Fortbildung bearbeiten"})
