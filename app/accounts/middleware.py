from django.http import HttpResponseForbidden
from .permissions import is_supervisor, is_read_only

class RoleAccessMiddleware:
    """Server-side coarse route guard. Individual sensitive views still perform object-level checks."""
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return self.get_response(request)
        p = request.path
        if is_supervisor(user):
            blocked = ("/warteliste/", "/dokumente/", "/statistiken/", "/audit/", "/system/backup/", "/admin/")
            if p.startswith(blocked):
                return HttpResponseForbidden("Für diesen Bereich besitzt die Rolle Betreuer keine Berechtigung.")
            if p.startswith("/betreuer/"):
                return HttpResponseForbidden("Die Betreuerverwaltung ist Jugendwarten und Administratoren vorbehalten.")
            if p.startswith("/mitglieder/") and request.method not in ("GET", "HEAD", "OPTIONS"):
                return HttpResponseForbidden("Betreuer dürfen Mitgliedsdaten nur lesen.")
        if is_read_only(user):
            if request.method not in ("GET", "HEAD", "OPTIONS"):
                return HttpResponseForbidden("Dieses Benutzerkonto besitzt nur Leserechte.")
            blocked=("/warteliste/", "/dokumente/", "/audit/", "/system/", "/admin/", "/vorfaelle/", "/betreuer/")
            if p.startswith(blocked): return HttpResponseForbidden("Keine Berechtigung für diesen Bereich.")
        return self.get_response(request)
