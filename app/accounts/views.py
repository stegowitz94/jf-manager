from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from audit.models import AuditEvent

from .forms import ProfileForm, StyledPasswordChangeForm


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil wurde gespeichert.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "accounts/profile.html", {"form": form})


@login_required
def password_change(request):
    if request.method == "POST":
        form = StyledPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            AuditEvent.objects.create(
                actor=request.user,
                action="Passwort geändert",
                object_type="Benutzerkonto",
                object_repr=request.user.get_username(),
                detail="Der Benutzer hat sein eigenes Passwort geändert.",
                path=request.path,
            )
            messages.success(request, "Passwort wurde erfolgreich geändert.")
            return redirect("accounts:profile")
    else:
        form = StyledPasswordChangeForm(user=request.user)

    return render(request, "accounts/password_change.html", {"form": form})
