from django import template
from django.utils.html import format_html

register = template.Library()

@register.filter
def stylize_title(value, css_class="altTitle"):
    """
    If value has ≥2 words → wrap the LAST word in <span class="{css_class}">…</span>
    If value has 1 word  → wrap the LAST HALF of the word in the span.
    """
    if not value:
        return ""
    s = str(value).strip()
    if not s:
        return ""

    parts = s.split()
    if len(parts) >= 2:
        head = " ".join(parts[:-1])
        tail = parts[-1]
        # head [space] <span>tail</span>
        return format_html('{} <span class="{}">{}</span>', head, css_class, tail)

    # Single word → split into two halves; last half goes in the span
    n = len(s)
    cut = (n // 2)  # e.g., "Portal" (6) -> 3|3; "Hello" (5) -> 2|3
    left, right = s[:cut], s[cut:]
    return format_html('{}<span class="{}">{}</span>', left, css_class, right)
