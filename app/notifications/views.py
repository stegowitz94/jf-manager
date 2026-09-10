import json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from .models import NotificationLog, PushSubscription, UserNotificationPreference
from .push import push_configured, send_push

@login_required
def log_list(request):
    pref,_=UserNotificationPreference.objects.get_or_create(user=request.user)
    return render(request,"notifications/list.html",{
        "logs":NotificationLog.objects.all()[:200], "preference":pref,
        "subscriptions":request.user.push_subscriptions.all(),
        "vapid_public_key":settings.WEBPUSH_VAPID_PUBLIC_KEY,
        "push_configured":push_configured(),
    })

@login_required
@require_POST
def save_preferences(request):
    pref,_=UserNotificationPreference.objects.get_or_create(user=request.user)
    for field in ("email_enabled","push_enabled","birthdays","absences","leave_end","upcoming_activity","scouting"):
        setattr(pref,field,field in request.POST)
    pref.save(); messages.success(request,"Benachrichtigungseinstellungen gespeichert.")
    return redirect("notifications:list")

@login_required
@require_POST
def subscribe(request):
    try: data=json.loads(request.body)
    except json.JSONDecodeError: return JsonResponse({"ok":False,"error":"Ungültige Daten"},status=400)
    keys=data.get("keys") or {}
    if not data.get("endpoint") or not keys.get("p256dh") or not keys.get("auth"):
        return JsonResponse({"ok":False,"error":"Unvollständiges Abonnement"},status=400)
    PushSubscription.objects.update_or_create(endpoint=data["endpoint"],defaults={"user":request.user,"p256dh":keys["p256dh"],"auth":keys["auth"],"user_agent":request.headers.get("User-Agent","")[:500]})
    pref,_=UserNotificationPreference.objects.get_or_create(user=request.user); pref.push_enabled=True; pref.save(update_fields=["push_enabled"])
    return JsonResponse({"ok":True})

@login_required
@require_POST
def unsubscribe(request):
    endpoint=request.POST.get("endpoint","")
    request.user.push_subscriptions.filter(endpoint=endpoint).delete()
    messages.success(request,"Push-Gerät wurde entfernt.")
    return redirect("notifications:list")

@login_required
@require_POST
def test_push(request):
    ok=0; errors=[]
    for sub in request.user.push_subscriptions.all():
        sent,error=send_push(sub,"JF-Manager Test","Push-Benachrichtigungen funktionieren.","/benachrichtigungen/")
        ok += int(sent)
        if error: errors.append(error)
    if ok: messages.success(request,f"Test-Push an {ok} Gerät(e) versendet.")
    else: messages.error(request,"Kein Push versendet: "+("; ".join(errors[:2]) or "Kein Gerät registriert"))
    return redirect("notifications:list")
