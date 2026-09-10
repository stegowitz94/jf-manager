from django.db import transaction

from members.models import Member
from supervisors.models import Supervisor

from .models import Attendance, SupervisorAttendance


@transaction.atomic
def initialize_attendance(activity, user=None):
    existing_member_ids = set(activity.attendances.values_list("member_id", flat=True))
    members = Member.objects.exclude(activity_status=Member.ActivityStatus.RESIGNED)
    to_create = []
    for member in members:
        if member.pk in existing_member_ids:
            continue
        if member.activity_status == Member.ActivityStatus.ON_LEAVE:
            status = Attendance.Status.EXCUSED
            source = Attendance.Source.LEAVE
        else:
            status = Attendance.Status.PRESENT
            source = Attendance.Source.DEFAULT
        to_create.append(
            Attendance(activity=activity, member=member, status=status, source=source, updated_by=user)
        )
    Attendance.objects.bulk_create(to_create)


@transaction.atomic
def initialize_supervisor_attendance(activity, user=None):
    existing_ids = set(activity.supervisor_attendances.values_list("supervisor_id", flat=True))
    supervisors = Supervisor.objects.exclude(activity_status=Supervisor.ActivityStatus.LEFT)
    to_create = []
    for supervisor in supervisors:
        if supervisor.pk in existing_ids:
            continue
        if supervisor.activity_status == Supervisor.ActivityStatus.ON_LEAVE:
            status = SupervisorAttendance.Status.EXCUSED
            source = SupervisorAttendance.Source.LEAVE
        else:
            status = SupervisorAttendance.Status.PRESENT
            source = SupervisorAttendance.Source.DEFAULT
        to_create.append(
            SupervisorAttendance(
                activity=activity,
                supervisor=supervisor,
                status=status,
                source=source,
                updated_by=user,
            )
        )
    SupervisorAttendance.objects.bulk_create(to_create)
