from django.conf import settings

from .models import ExternalLink, AppSettings


def external_links(request):
    return {
        "external_links": ExternalLink.objects.filter(visible=True),
        "app_settings": AppSettings.load(),
        "source_code_url": getattr(settings, "JF_SOURCE_CODE_URL", ""),
    }
