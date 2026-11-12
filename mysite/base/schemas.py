from django.conf import settings


organisation_schema = {
    "@context": "http://schema.org",
    "@type": "Organization",
    "name": f"{settings.SITE_ROOT}",
    "url": f"{settings.BASE_URI}",
    "logo": f"{settings.BASE_URI}/static/assets/img/logos/ventanita.avif",
    "image": f"{settings.BASE_URI}/static/assets/img/logos/ventanita.avif",
    "description": "Plataforma de viajes en Argentina 🇦🇷",
    "email": f"{settings.DEFAULT_FROM_EMAIL}",
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
        "email": f"{settings.DEFAULT_FROM_EMAIL}",
    },
    "sameAs": [],
}
