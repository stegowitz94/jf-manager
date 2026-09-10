from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from members.models import Member

from .models import Activity, Attendance, SupervisorAttendance
from .services import initialize_attendance, initialize_supervisor_attendance


class AttendanceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="wart", password="test-password")
        self.active = Member.objects.create(sequential_number=1, first_name="Max", last_name="Aktiv", birth_date="2012-01-01")
        self.leave = Member.objects.create(sequential_number=2, first_name="Mia", last_name="Pause", birth_date="2012-02-01", activity_status=Member.ActivityStatus.ON_LEAVE)
        self.activity = Activity.objects.create(title="Fahrzeugkunde", starts_at=timezone.now(), created_by=self.user)

    def test_initialization_uses_mobile_friendly_defaults(self):
        initialize_attendance(self.activity, self.user)
        self.assertEqual(self.activity.attendances.get(member=self.active).status, Attendance.Status.PRESENT)
        self.assertEqual(self.activity.attendances.get(member=self.leave).status, Attendance.Status.EXCUSED)

    def test_logged_in_user_can_update_attendance(self):
        initialize_attendance(self.activity, self.user)
        row = self.activity.attendances.get(member=self.active)
        self.client.force_login(self.user)
        response = self.client.post(reverse("activities:attendance_update", args=(self.activity.pk, row.pk)), {"status": Attendance.Status.UNEXCUSED})
        self.assertEqual(response.status_code, 200)
        row.refresh_from_db()
        self.assertEqual(row.status, Attendance.Status.UNEXCUSED)

class ActivityDefaultTimesTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        self.user = get_user_model().objects.create_user(username="times-user", password="secret123")
        self.client.force_login(self.user)

    def test_group_defaults_endpoint(self):
        response = self.client.get("/termine/standardzeiten/", {"type": Activity.ActivityType.GROUP})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["start"], "17:15")
        self.assertEqual(response.json()["end"], "18:45")

    def test_create_form_uses_group_default_times(self):
        response = self.client.get("/termine/neu/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "T17:15")
        self.assertContains(response, "T18:45")


class SupervisorAttendanceTests(TestCase):
    def setUp(self):
        from supervisors.models import Supervisor
        self.user = get_user_model().objects.create_user(username="supervisor-wart", password="test-password")
        self.active = Supervisor.objects.create(sequential_number=1, first_name="Anna", last_name="Aktiv")
        self.leave = Supervisor.objects.create(sequential_number=2, first_name="Ben", last_name="Pause", activity_status=Supervisor.ActivityStatus.ON_LEAVE)
        self.left = Supervisor.objects.create(sequential_number=3, first_name="Chris", last_name="Ausgeschieden", activity_status=Supervisor.ActivityStatus.LEFT)
        self.activity = Activity.objects.create(title="TH-Ausbildung", starts_at=timezone.now(), created_by=self.user)

    def test_initialization_excludes_left_and_respects_leave(self):
        initialize_supervisor_attendance(self.activity, self.user)
        self.assertEqual(self.activity.supervisor_attendances.count(), 2)
        self.assertEqual(self.activity.supervisor_attendances.get(supervisor=self.active).status, SupervisorAttendance.Status.PRESENT)
        self.assertEqual(self.activity.supervisor_attendances.get(supervisor=self.leave).status, SupervisorAttendance.Status.EXCUSED)
        self.assertFalse(self.activity.supervisor_attendances.filter(supervisor=self.left).exists())

    def test_logged_in_user_can_update_supervisor_attendance(self):
        initialize_supervisor_attendance(self.activity, self.user)
        row = self.activity.supervisor_attendances.get(supervisor=self.active)
        self.client.force_login(self.user)
        response = self.client.post(reverse("activities:supervisor_attendance_update", args=(self.activity.pk, row.pk)), {"status": SupervisorAttendance.Status.UNEXCUSED})
        self.assertEqual(response.status_code, 200)
        row.refresh_from_db()
        self.assertEqual(row.status, SupervisorAttendance.Status.UNEXCUSED)
