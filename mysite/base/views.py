import logging

from django.conf import settings
from django.http import FileResponse, HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView

from wagtail.contrib.forms.views import SubmissionsListView
from wagtail.images import get_image_model
from wagtail.models.sites import Site


logger = logging.getLogger(__name__)

ImageModel = get_image_model()


@require_GET
@cache_control(max_age=60 * 60 * 24, immutable=True, public=True)  # one day
def favicon(request: HttpRequest) -> FileResponse:
    """
    You might wonder why you need a separate view, rather than relying on Django’s staticfiles app.
    The reason is that staticfiles only serves files from within the STATIC_URL prefix, like static/.

    Thus staticfiles can only serve /static/favicon.ico,
    whilst the favicon needs to be served at exactly /favicon.ico (without a <link>).

    Say if the project is accessed at an endpoint that returns a simple JSON and doesn't use the
    base.html file then the favicon won't show up.

    This endpoint acts as a fall back to supply the necessary icon at /favicon.ico
    """

    static = "static" if settings.DEBUG else "staticfiles"

    file = (
        settings.BASE_DIR / static / "assets" / "img" / "logos" / "favicon.ico"
    ).open("rb")
    return FileResponse(file, headers={"Content-Type": "image/x-icon"})


class RobotsView(TemplateView):
    """
    Render a robots.txt with sitemap urls
    """

    content_type = "text/plain"
    template_name = "robots.txt"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = context["view"].request
        context["wagtail_site"] = Site.find_for_request(request)
        return context


class IndexNow(TemplateView):
    template_name = "indexnow_key.txt"
    content_type = "text/plain"
    extra_context = {"key": settings.INDEXNOW_KEY}


class CustomSubmissionsListView(SubmissionsListView):
    """
    Custom List view to show the preview of an image in the admin.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.is_export:
            # In export mode no need to render thumbnail images
            logger.info("export requested...")
            return context

        # generate a list of field types, the first being the injected 'submission date'
        field_types = ["submission_date"] + [
            field.field_type for field in self.form_page.get_form_fields()
        ]
        data_rows = context["data_rows"]

        for data_row in data_rows:
            fields = data_row["fields"]

            for idx, (value, field_type) in enumerate(
                zip(fields, field_types)
            ):
                if field_type == "image" and value:
                    image = ImageModel.objects.get(pk=value)
                    rendition = image.get_rendition(
                        "fill-100x75|jpegquality-40"
                    )
                    preview_url = rendition.url
                    url = reverse("wagtailimages:edit", args=(image.id,))
                    # build up a link to the image, using the image title & id
                    fields[idx] = format_html(
                        "<a href='{}'><img alt='Uploaded image - {}' src='{}' /></br>{} ({})</a>",
                        url,
                        image.title,
                        preview_url,
                        image.title,
                        value,
                    )

        return context
