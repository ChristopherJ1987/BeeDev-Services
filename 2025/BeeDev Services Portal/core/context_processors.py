# core/context_processors.py
from django.conf import settings

def beedev_defaults(request):
    return {
        "brand": "BeeDev Services",
        "nav_show_admin": request.user.is_staff if request.user.is_authenticated else False,
        "year": 2025,
    }

def branding(request):
    return {
        "brand": {
            "name":        getattr(settings, "BRAND_NAME", "BeeDev Services"),
            "subtitle":    getattr(settings, "BRAND_SUBTITLE", ""),
            "logo_static": getattr(settings, "BRAND_LOGO_STATIC", "images/altLogo.png"),
            "favicon":     getattr(settings, "BRAND_FAVICON", "images/favicon.png"),
            "website":     getattr(settings, "BRAND_WEBSITE", ""),
            "email":       getattr(settings, "BRAND_EMAIL", ""),
            "phone":       getattr(settings, "BRAND_PHONE", ""),
            "address":     getattr(settings, "BRAND_ADDRESS", ""),
        }
    }