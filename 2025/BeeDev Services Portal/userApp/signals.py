from django.db.models.signals import post_migrate, post_save, pre_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import ClientProfile, EmployeeProfile  # if you created EmployeeProfile

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

    # --- profiles (optional; keep if you're using both profiles)
    old = getattr(instance, "_old_role", None)
    is_client      = (instance.role == User.Roles.CLIENT)
    is_companyside = (instance.role in (User.Roles.EMPLOYEE, User.Roles.ADMIN, User.Roles.OWNER))

    if created or old != instance.role:
        if is_client:
            ClientProfile.objects.get_or_create(user=instance)
            EmployeeProfile.objects.filter(user=instance).delete()
        elif is_companyside:
            EmployeeProfile.objects.get_or_create(user=instance)
            ClientProfile.objects.filter(user=instance).delete()

    # --- is_staff auto-manage (role OR HR group)
    in_hr = instance.groups.filter(name="HR").exists()
    desired_staff = is_companyside or in_hr
    if instance.is_staff != desired_staff:
        # Use update() to avoid recursive save signals
        instance.__class__.objects.filter(pk=instance.pk).update(is_staff=desired_staff)

@receiver(m2m_changed, sender=User.groups.through)
def ensure_staff_follows_hr_group(sender, instance: User, action, reverse, model, pk_set, **kwargs):
    # When HR group membership changes, keep is_staff in sync
    if action in {"post_add", "post_remove", "post_clear"}:
        company_roles = {getattr(instance.Roles, "EMPLOYEE", "EMPLOYEE"),
                         getattr(instance.Roles, "ADMIN", "ADMIN"),
                         getattr(instance.Roles, "OWNER", "OWNER")}
        in_hr = instance.groups.filter(name="HR").exists()
        desired_staff = (instance.role in company_roles) or in_hr
        if instance.is_staff != desired_staff:
            instance.__class__.objects.filter(pk=instance.pk).update(is_staff=desired_staff)
