import re
from django import template

register = template.Library()


@register.filter
def phone_uri(value):
    """Normalize a displayed phone number for a tel: link without changing storage."""
    if not value:
        return ""
    raw = str(value).strip()
    prefix = "+" if raw.startswith("+") else ""
    digits = re.sub(r"\D", "", raw)
    return f"{prefix}{digits}"


@register.filter
def address_uri(value):
    from urllib.parse import quote_plus
    return quote_plus(str(value or "").strip())
