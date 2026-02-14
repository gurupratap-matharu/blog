import json

from django import template
from django.utils.html import mark_safe


register = template.Library()


@register.simple_tag
def global_schema_markup(site):
    """
    Generates a site wide schema markup for Ventanita. At the moment
    purposely hardcoded to avoid DB query as most values are generally constant.
    """

    organisation_schema = {
        "@context": "http://schema.org",
        "@type": "Organization",
        "name": "Ventanita",
        "url": "https://ventanita.com.ar",
        "logo": "https://ventanita.com.ar/static/assets/img/logos/logo.avif",
        "image": "https://ventanita.com.ar/static/assets/img/logos/logo.avif",
        "description": "Plataforma de viajes en Argentina 🇦🇷",
        "email": "support@ventanita.com.ar",
        "telephone": "+54-11-5025-4191",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Uspallata 471",
            "addressLocality": "Buenos Aires",
            "addressCountry": "AR",
            "addressRegion": "CABA",
            "postalCode": "1143",
        },
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+54-911-5025-4191",
            "email": "support@ventanita.com.ar",
        },
        "sameAs": [],
    }

    schema = f"{json.dumps(organisation_schema)}"
    return mark_safe(schema)
