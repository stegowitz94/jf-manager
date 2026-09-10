from django.shortcuts import redirect
from django.db.utils import OperationalError, ProgrammingError
from .models import AppSettings


class SetupRequiredMiddleware:
    """Send an unconfigured, freshly migrated instance to the setup wizard."""
    ALLOWED_PREFIXES = ("/setup/", "/health/", "/static/", "/service-worker.js", "/manifest.webmanifest", "/offline/")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(self.ALLOWED_PREFIXES):
            return self.get_response(request)
        try:
            configured = AppSettings.objects.filter(pk=1, setup_complete=True).exists()
        except (OperationalError, ProgrammingError):
            # Startup/migration phase: don't turn a transient DB state into a redirect loop.
            return self.get_response(request)
        if not configured:
            return redirect("core:setup")
        return self.get_response(request)
