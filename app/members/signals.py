from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Member, MemberStatusHistory


@receiver(pre_save, sender=Member)
def remember_previous_status(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_activity_status = None
        return
    instance._previous_activity_status = sender.objects.filter(pk=instance.pk).values_list("activity_status", flat=True).first()


@receiver(post_save, sender=Member)
def maintain_status_history(sender, instance, created, **kwargs):
    previous = getattr(instance, "_previous_activity_status", None)
    if created or previous != instance.activity_status:
        MemberStatusHistory.objects.create(
            member=instance,
            status=instance.activity_status,
            valid_from=timezone.localdate(),
        )
