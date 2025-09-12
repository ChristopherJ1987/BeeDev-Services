from django.db.models.signals import post_migrate, post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import ClientProfile, EmployeeProfile

ROLE_GROUPS = ["Owner", "Admin", "Employee", "Client"]
AUX_GROUPS  = ["HR"]

User = get_user_model()

@receiver(post_migrate)
def ensure_default_groups(sender, **kwargs):
    for name in ROLE_GROUPS + AUX_GROUPS:
        Group.objects.get_or_create(name=name)

@receiver(pre_save, sender=settings.AUTH_USER_MODEL)
def cache_old_role(sender, instance: User, **kwargs):
    instance._old_role = None
    if instance.pk:
        try:
            instance._old_role = sender.objects.get(pk=instance.pk).role
        except sender.DoesNotExist:
            pass

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def sync_role_to_group_and_profiles(sender, instance: User, created, **kwargs):
    # --- role -> group sync (no HR here)
    role_to_group = {
        "OWNER": "Owner",
        "ADMIN": "Admin",
        "EMPLOYEE": "Employee",
        "CLIENT": "Client",
    }
    target = role_to_group.get(instance.role)
    if target:
        role_group_qs = Group.objects.filter(name__in=ROLE_GROUPS)
        instance.groups.remove(*role_group_qs)
        g, _ = Group.objects.get_or_create(name=target)
        instance.groups.add(g)

    # --- profiles (mutually exclusive)
    old = getattr(instance, "_old_role", None)
    is_client      = (instance.role == User.Roles.CLIENT)
    is_companyside = (instance.role in (User.Roles.EMPLOYEE, User.Roles.ADMIN, User.Roles.OWNER))

    # CREATE proper profile on first creation or role change
    if created or old != instance.role:
        if is_client:
            ClientProfile.objects.get_or_create(user=instance)
            EmployeeProfile.objects.filter(user=instance).delete()
        elif is_companyside:
            EmployeeProfile.objects.get_or_create(user=instance)
            ClientProfile.objects.filter(user=instance).delete()

    # Optional: if you prefer to keep old profiles (not delete), comment out the deletes above.
