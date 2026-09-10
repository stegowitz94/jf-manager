import json
from django.conf import settings


def push_configured():
    return bool(settings.WEBPUSH_VAPID_PUBLIC_KEY and settings.WEBPUSH_VAPID_PRIVATE_KEY)


def send_push(subscription, title, body, url="/"):
    if not push_configured():
        return False, "VAPID ist nicht konfiguriert"
    from pywebpush import webpush, WebPushException
    try:
        webpush(
            subscription_info={
                "endpoint": subscription.endpoint,
                "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
            },
            data=json.dumps({"title": title, "body": body, "url": url}),
            vapid_private_key=settings.WEBPUSH_VAPID_PRIVATE_KEY,
            vapid_claims={"sub": settings.WEBPUSH_VAPID_CLAIMS_EMAIL},
            ttl=3600,
        )
        return True, ""
    except WebPushException as exc:
        if getattr(exc.response, "status_code", None) in (404, 410):
            subscription.delete()
        return False, str(exc)
