from django.conf import settings
from django.views.decorators.cache import cache_control


def get_cache_control_kwargs():
    """
    Build cache control kwargs based on cache settings
    which can be applied to most content pages.
    """

    s_max_age = getattr(settings, "CACHE_CONTROL_S_MAX_AGE", None)
    stale_while_revalidate = getattr(
        settings, "CACHE_CONTROL_STALE_WHILE_REVALIDATE", None
    )

    cache_control_kwargs = {
        "s_max_age": s_max_age,
        "stale_while_revalidate": stale_while_revalidate,
        "public": True,
    }

    print(f"cache_control_kwargs:{cache_control_kwargs}")

    return {k: v for k, v in cache_control_kwargs.items() if v is not None}


def get_default_cache_control_decorator():
    """
    Get cache control decorator that can be applied to views as a sane
    default for normal content pages.
    """

    cache_control_kwargs = get_cache_control_kwargs()
    return cache_control(**cache_control_kwargs)
