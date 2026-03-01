from django.conf import settings
from django.http import HttpRequest


def branding(request: HttpRequest) -> dict[str, str | None]:
    return {
        "site_name": settings.SITE_NAME,
        "site_root": settings.SITE_ROOT,
        "site_logo_url": settings.SITE_LOGO_URL,
    }
