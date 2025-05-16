from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls

from base.views import RobotsView, favicon
from debug_toolbar.toolbar import debug_toolbar_urls
from search import views as search_views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("private/", include(wagtailadmin_urls)),
    path("accounts/", include("allauth.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("documents/", include(wagtaildocs_urls)),
    path("trips/", include("trips.urls")),
    path("orders/", include("orders.urls")),
    path("sitemap.xml", sitemap),
    path("favicon.ico", favicon),
    path("robots.txt", RobotsView.as_view()),
    path("styleguide/", TemplateView.as_view(template_name="styleguide.html")),
]


if not settings.TESTING:
    urlpatterns = [*urlpatterns] + debug_toolbar_urls()

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

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
    prefix_default_language=False,
)
