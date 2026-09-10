from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from accounts.models import User
from accounts.permissions import is_leadership, is_supervisor, incident_visible_to, incident_editable_by
from incidents.models import Incident

class PermissionRulesTest(TestCase):
    def test_roles(self):
        lead=User(username="lead",role=User.Role.YOUTH_WARDEN); sup=User(username="sup",role=User.Role.SUPERVISOR)
        self.assertTrue(is_leadership(lead)); self.assertTrue(is_supervisor(sup)); self.assertFalse(is_leadership(sup))
    def test_incident_windows(self):
        sup=User.objects.create_user("sup",password="A-long-test-password-123",role=User.Role.SUPERVISOR)
        obj=Incident.objects.create(occurred_at=timezone.now(),title="Test",documentation="Test",created_by=sup)
        self.assertTrue(incident_visible_to(sup,obj)); self.assertTrue(incident_editable_by(sup,obj))
        Incident.objects.filter(pk=obj.pk).update(created_at=timezone.now()-timedelta(days=31)); obj.refresh_from_db()
        self.assertFalse(incident_visible_to(sup,obj))
