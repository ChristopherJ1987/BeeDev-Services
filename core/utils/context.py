# core/context.py
from typing import Optional, Dict, Any
from django.utils import timezone
from django.db.models import Q

DEFAULT_SITE_SUFFIX = "BeeDev Services"

def _audiences_for_user(user) -> list[str]:
    if not getattr(user, "is_authenticated", False):
        return ["PUBLIC", "ALL"]
    try:
        emp_roles = {user.Roles.EMPLOYEE, user.Roles.ADMIN, user.Roles.OWNER, user.Roles.HR}
        role = getattr(user, "role", None)
        if role in emp_roles:
            return ["EMPLOYEE", "ALL"]
        if role == user.Roles.CLIENT:
            return ["CLIENT", "ALL"]
    except Exception:
        pass
    return ["ALL"]

def _announce_and_version(request):
    """
    Lazy-import announceApp so core doesn't hard-depend on it.
    Returns (marquee_notice, marquee_list, app_version_str, version_obj)
    """
    try:
        from announceApp.models import Announcement, Version
    except Exception:
        # App not installed yet; safe fallbacks
        return None, [], "dev", None

    now = timezone.now()
    audiences = _audiences_for_user(getattr(request, "user", None))

    ann_qs = (
        Announcement.objects
        .filter(is_active=True, audience__in=audiences)
        .filter(Q(starts_at__isnull=True) | Q(starts_at__lte=now))
        .filter(Q(ends_at__isnull=True) | Q(ends_at__gte=now))
        .order_by("priority", "-updated_at")
    )
    marquee_list = list(ann_qs[:5])
    marquee_notice = marquee_list[0] if marquee_list else None

    v = Version.objects.order_by("-date_of_release", "-updated_at").first()
    app_version = v.version_num if v else "dev"

    return marquee_notice, marquee_list, app_version, v

def base_ctx(
    request,
    *,
    title: Optional[str] = None,
    add_suffix: bool = True,
    **extra: Any
) -> Dict[str, Any]:
    """
    Reusable per-view context additions.
    - `title`: full document title (defaults to "<title_short> - BeeDev Services")
    - `title_short`: plain page title without suffix (safe for H1s)
    - `site_name`: the suffix string ("BeeDev Services")
    - NEW:
      - `marquee_notice`: first matching Announcement for the current user/audience
      - `marquee_list`: up to 5 current Announcements (use if you want to render multiple)
      - `app_version`: string for footer (e.g., "0.5.2")
      - `app_version_obj`: Version instance (gives you date_of_release/info)
    """
    site_name = DEFAULT_SITE_SUFFIX
    title_short = (title or "").strip()

    if add_suffix:
        full_title = f"{title_short} - {site_name}" if title_short else site_name
    else:
        full_title = title_short or site_name

    marquee_notice, marquee_list, app_version, app_version_obj = _announce_and_version(request)

    ctx = {
        "title": full_title,
        "title_short": title_short,
        "site_name": site_name,
        "marquee_notice": marquee_notice,
        "marquee_list": marquee_list,
        "app_version": app_version,
        "app_version_obj": app_version_obj,
    }
    ctx.update(extra)
    return ctx


class CommonContextMixin:
    common_title: Optional[str] = None
    common_add_suffix: bool = True

    def get_common_ctx(self):
        return base_ctx(self.request, title=self.common_title, add_suffix=self.common_add_suffix)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(self.get_common_ctx())
        return ctx
