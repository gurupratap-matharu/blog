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
        "@type": "Organization",
        "@id": "https://ventanita.com.ar/#organization",
        "name": "Ventanita",
        "url": "https://ventanita.com.ar",
        "logo": {
            "@type": "ImageObject",
            "inLanguage": "es",
            "@id": "https://ventanita.com.ar/blog/#/schema/logo/image/",
            "url": "https://ventanita.com.ar/static/assets/img/logos/logo.avif",
            "contentUrl": "https://ventanita.com.ar/static/assets/img/logos/logo.avif",
            "width": 2048,
            "height": 768,
            "caption": "Ventanita",
        },
        "image": {"@id": "https://ventanita.com.ar/blog/#/schema/logo/image/"},
        "sameAs": [],
    }

    website_schema = {
        "@type": "WebSite",
        "@id": "https://ventanita.com.ar/#website",
        "url": "https://ventanita.com.ar/",
        "name": "Ventanita",
        "description": "Plataforma de viajes en Argentina",
        "publisher": {"@id": "https://ventanita.com.ar/#organization"},
        "inLanguage": "es",
    }

    schema = f"{json.dumps(organisation_schema)}, {json.dumps(website_schema)},"
    return mark_safe(schema)
