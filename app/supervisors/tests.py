from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Supervisor, SupervisorFunction


class SupervisorTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="test", password="secret-test-password")
        self.client.force_login(self.user)

    def test_default_functions_exist(self):
        expected = {"Jugendfeuerwehrwart", "Stellvertretender Jugendfeuerwehrwart", "Betreuer", "Hilfsbetreuer", "Maschinist"}
        self.assertTrue(expected.issubset(set(SupervisorFunction.objects.values_list("name", flat=True))))

    def test_supervisor_list_requires_login_and_renders(self):
        Supervisor.objects.create(sequential_number=1, first_name="Max", last_name="Muster")
        response = self.client.get(reverse("supervisors:list"))
        self.assertContains(response, "Max Muster")
