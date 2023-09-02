from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls
from django.conf.urls.i18n import i18n_patterns
from search import views as search_views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("sitemap.xml", sitemap),
    path("__debug__/", include("debug_toolbar.urls")),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.views.generic import TemplateView
    from django.views.generic.base import RedirectView

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Serve favicon at /favicon.ico
    urlpatterns += [
        path(
            "favicon.ico",
            RedirectView.as_view(url=settings.STATIC_URL + "assets/img/favicon.png"),
        )
    ]

    # Add routes to test error templates
    urlpatterns += [
        path("test404/", TemplateView.as_view(template_name="404.html")),
        path("test500/", TemplateView.as_view(template_name="500.html")),
    ]

urlpatterns += i18n_patterns(
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("search/", search_views.search, name="search"),
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    # path("pages/", include(wagtail_urls)),
)
