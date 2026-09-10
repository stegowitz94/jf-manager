from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class HealthTests(TestCase):
    def test_health_endpoint(self):
        response = self.client.get(reverse("core:health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class DashboardTests(TestCase):
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 302)


class SystemStatusTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin = user_model.objects.create_user(username="admin", password="test", role="admin")
        self.warden = user_model.objects.create_user(username="warden", password="test", role="youth_warden")

    def test_system_status_requires_login(self):
        response = self.client.get(reverse("core:system_status"))
        self.assertEqual(response.status_code, 302)

    def test_system_status_rejects_non_admin(self):
        self.client.force_login(self.warden)
        response = self.client.get(reverse("core:system_status"))
        self.assertEqual(response.status_code, 403)

    @patch("core.views.current_app.control.inspect")
    @patch("core.views.redis.Redis.from_url")
    def test_system_status_allows_admin(self, redis_from_url, inspect):
        redis_from_url.return_value.ping.return_value = True
        inspect.return_value.ping.return_value = {"worker": {"ok": "pong"}}
        self.client.force_login(self.admin)
        response = self.client.get(reverse("core:system_status"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Systemstatus")


class ProductivityDefaultsTests(TestCase):
    def test_scouting_defaults(self):
        from core.models import AppSettings
        settings_obj = AppSettings.load()
        self.assertEqual(settings_obj.scouting_age_years, 16)
        self.assertEqual(settings_obj.scouting_lead_months, 6)

    def test_dashboard_preference_has_new_widgets(self):
        from core.models import DashboardPreference
        user = get_user_model().objects.create_user(username="widgets", password="test")
        preference = DashboardPreference.objects.create(user=user)
        self.assertTrue(preference.show_today)
        self.assertTrue(preference.show_scouting)
        self.assertTrue(preference.show_recent_changes)
