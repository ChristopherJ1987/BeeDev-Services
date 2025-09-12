# core/context.py (or wherever this lives)
from typing import Optional, Dict, Any

DEFAULT_SITE_SUFFIX = "BeeDev Services"

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
    """
    site_name = DEFAULT_SITE_SUFFIX
    title_short = (title or "").strip()

    if add_suffix:
        full_title = f"{title_short} - {site_name}" if title_short else site_name
    else:
        full_title = title_short or site_name

    ctx = {
        "title": full_title,       # browser/tab title (with suffix by default)
        "title_short": title_short,  # plain title for on-page headings
        "site_name": site_name,
    }
    ctx.update(extra)
    return ctx


class CommonContextMixin:
    """
    Mixin for CBVs to layer common context on top of super().get_context_data().
    """
    common_title: Optional[str] = None
    common_add_suffix: bool = True  # NEW

    def get_common_ctx(self):
        return base_ctx(self.request, title=self.common_title, add_suffix=self.common_add_suffix)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(self.get_common_ctx())
        return ctx
