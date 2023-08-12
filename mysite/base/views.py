import logging

from django.urls import reverse
from django.utils.html import format_html

from wagtail.contrib.forms.views import SubmissionsListView
from wagtail.images import get_image_model

logger = logging.getLogger(__name__)

ImageModel = get_image_model()


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

            for idx, (value, field_type) in enumerate(zip(fields, field_types)):
                if field_type == "image" and value:
                    image = ImageModel.objects.get(pk=value)
                    rendition = image.get_rendition("fill-100x75|jpegquality-40")
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
