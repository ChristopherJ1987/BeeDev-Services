from typing import Optional, Dict, Any

DEFAULT_SITE_SUFFIX = "BeeDev Services"

def base_ctx(request, *, title: Optional[str] = None, **extra: Any) -> Dict[str, Any]:
    """
    Reusable per-view context additions.
    Automatically appends " - BeeDev Services" to titles unless None.
    """
    if title:
        full_title = f"{title} - {DEFAULT_SITE_SUFFIX}"
    else:
        full_title = DEFAULT_SITE_SUFFIX

    ctx = {
        "title": full_title,
    }
    ctx.update(extra)
    return ctx


class CommonContextMixin:
    """
    Mixin for CBVs to layer common context on top of super().get_context_data().
    Override `common_title` or `get_common_ctx` per view as needed.
    """
    common_title: Optional[str] = None

    def get_common_ctx(self):
        return base_ctx(self.request, title=self.common_title)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(self.get_common_ctx())
        return ctx
