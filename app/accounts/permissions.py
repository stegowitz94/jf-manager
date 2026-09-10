from datetime import timedelta
from django.utils import timezone

LEADERSHIP_ROLES = {"admin", "youth_warden", "deputy_youth_warden"}

def role(user): return getattr(user, "role", "")
def is_admin(user): return bool(user.is_authenticated and (user.is_superuser or role(user) == "admin"))
def is_leadership(user): return bool(user.is_authenticated and (user.is_superuser or role(user) in LEADERSHIP_ROLES))
def is_supervisor(user): return bool(user.is_authenticated and role(user) == "supervisor")
def is_read_only(user): return bool(user.is_authenticated and role(user) == "read_only")
def can_view_members(user): return bool(user.is_authenticated and (is_leadership(user) or is_supervisor(user) or is_read_only(user)))
def can_manage_members(user): return is_leadership(user)
def can_manage_activities(user): return bool(is_leadership(user) or is_supervisor(user))
def can_view_sensitive_health(user): return is_leadership(user)
def can_create_incident(user): return bool(is_leadership(user) or is_supervisor(user))
def incident_visible_to(user, incident):
    if is_leadership(user): return True
    if not is_supervisor(user) or incident.created_by_id != user.id: return False
    return incident.created_at >= timezone.now() - timedelta(days=30)
def incident_editable_by(user, incident):
    if is_leadership(user): return True
    if not is_supervisor(user) or incident.created_by_id != user.id: return False
    return incident.created_at >= timezone.now() - timedelta(hours=24)
