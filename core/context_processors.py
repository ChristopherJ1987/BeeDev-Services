# core/context_processors.py
def beedev_defaults(request):
    return {
        "brand": "BeeDev Services",
        "nav_show_admin": request.user.is_staff if request.user.is_authenticated else False,
        "year": 2025,
    }
