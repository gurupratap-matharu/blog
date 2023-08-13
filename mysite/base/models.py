import logging
from os.path import splitext

from django.contrib import messages
from django.db import models
from django.forms import widgets
from django.shortcuts import redirect

from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.forms.forms import FormBuilder
from wagtail.contrib.forms.models import (
    FORM_FIELD_CHOICES,
    AbstractEmailForm,
    AbstractFormField,
)
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    BaseSiteSetting,
    register_setting,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model
from wagtail.images.fields import WagtailImageField
from wagtail.models import Collection, Page

from base.blocks import BaseStreamBlock
from base.views import CustomSubmissionsListView
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

logger = logging.getLogger(__name__)

ImageModel = get_image_model()


class StandardPage(Page):
    """
    A generic content page which we can use for any page that only needs a title, image, introduction and a body field.

    Some examples are typical static pages like
    about, terms, privacy, etc.
    """

    page_description = "Use this to build a simple or generic page"

    introduction = models.TextField(help_text="Text to describe the page", blank=True)

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px to 3000px.",
    )

    body = StreamField(
        BaseStreamBlock(), verbose_name="Page body", blank=True, use_json_field=True
    )

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("image"),
        FieldPanel("body"),
    ]


class FormField(AbstractFormField):
    """
    One FormPage can have many FormFields. Here we declare the parentalkey (foreign key)
    for our form.
    """

    field_type = models.CharField(
        verbose_name="field type",
        max_length=16,
        choices=list(FORM_FIELD_CHOICES) + [("image", "Upload Image")],
    )

    page = ParentalKey("FormPage", related_name="form_fields", on_delete=models.CASCADE)


class CustomFormBuilder(FormBuilder):
    def create_image_field(self, field, options):
        return WagtailImageField(**options)


class FormPage(AbstractEmailForm):
    page_description = "Use this page to create a simple form"
    form_builder = CustomFormBuilder
    submissions_list_view_class = CustomSubmissionsListView

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = StreamField(BaseStreamBlock(), use_json_field=True, blank=True)
    thank_you_text = RichTextField(blank=True)

    uploaded_image_collection = models.ForeignKey(
        "wagtailcore.Collection",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    # Veer note how we include the FormField obj via an InlinePanel using the
    # related_name value
    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel("image"),
        FieldPanel("body"),
        InlinePanel("form_fields", heading="Form fields", label="Field"),
        FieldPanel("thank_you_text"),
        FieldPanel("uploaded_image_collection"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("from_address"),
                        FieldPanel("to_address"),
                    ]
                ),
                FieldPanel("subject"),
            ],
            "Email",
        ),
    ]

    def get_context(self, request, *args, **kwargs):
        """
        Find if the form on this page instance has an image upload in it.
        """

        context = super().get_context(request, *args, **kwargs)
        context["has_upload"] = any(
            f.field_type == "image" for f in self.form_fields.all()
        )
        return context

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)

        for name, field in form.fields.items():
            if isinstance(field.widget, widgets.Textarea):
                field.widget.attrs.update({"rows": "5"})

            attrs = field.widget.attrs
            css_classes = attrs.get("class", "").split()
            css_classes.append("form-control")
            attrs.update({"class": " ".join(css_classes)})

        return form

    @staticmethod
    def get_image_title(filename):
        """
        Generates a usable title from the filename of an image upload.
        Note: The filename will be provided as a 'path/to/file.jpg'
        """

        if not filename:
            return

        result = splitext(filename)[0]
        result = result.replace("-", " ").replace("_", " ").title()

        logger.info("image_title: %s" % result)

        return result.title()

    def get_uploaded_image_collection(self):
        """
        Returns a Wagtail Collection, using this form's saved value if present,
        otherwise returns the 'Root' Collection.
        """

        collection = self.uploaded_image_collection
        return collection or Collection.get_first_root_node()

    def process_form_submission(self, form):
        """
        If an Image upload is found, pull out the files data, create an actual
        Wagtail Image and reference its ID in the stored form response.
        """

        cleaned_data = form.cleaned_data

        logger.info("cleaned_data:%s" % cleaned_data)

        for name, field in form.fields.items():
            if isinstance(field, WagtailImageField):
                image_file_data = cleaned_data[name]

                if image_file_data:
                    kwargs = {
                        "file": cleaned_data[name],
                        "title": self.get_image_title(cleaned_data[name].name),
                        "collection": self.get_uploaded_image_collection(),
                    }

                    if form.user and not form.user.is_anonymous:
                        kwargs["uploaded_by_user"] = form.user

                    logger.info("kwargs:%s" % kwargs)
                    logger.info("creating image...")

                    image = ImageModel(**kwargs)
                    image.save()
                    # saving the image id
                    # alternatively we can store a path to the image via image.get_rendition

                    logger.info("created image:%s..." % image.pk)

                    cleaned_data.update({name: image.pk})

                else:
                    # remove the value from the data
                    logger.warn("image_file_data is None...")
                    del cleaned_data[name]

        submission = self.get_submission_class().objects.create(
            form_data=cleaned_data, page=self
        )

        logger.info("submission:%s" % submission)

        # important: if extending AbstractEmailForm, email logic must be re-added here
        if self.to_address:
            self.send_mail(form)

        return submission

    def render_landing_page(self, request, form_submission=None, *args, **kwargs):
        """
        Redirect user to home page after successful submission.
        """

        url = "/"
        # if a form_submission instance is available, append the id to URL
        # when previewing landing page, there will not be a form_submission instance
        if form_submission:
            url += "?id=%s" % form_submission.id

        messages.success(request, "Message sent successfully! 🙌")
        return redirect(url, permanent=False)


@register_setting
class GenericSettings(ClusterableModel, BaseGenericSetting):
    twitter_url = models.URLField(verbose_name="Twitter URL", blank=True)
    facebook_url = models.URLField(verbose_name="Facebook URL", blank=True)
    instagram_url = models.URLField(verbose_name="Instagram URL", blank=True)
    organisation_url = models.URLField(verbose_name="Organisation URL", blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("twitter_url"),
                FieldPanel("facebook_url"),
                FieldPanel("instagram_url"),
                FieldPanel("organisation_url"),
            ],
            "Social Links",
        )
    ]


@register_setting
class SiteSettings(BaseSiteSetting):
    title_suffix = models.CharField(
        verbose_name="Title suffix",
        max_length=255,
        help_text="The suffix for the title meta tag e.g. ' | The Falcon Blog'",
        default="Book Bus tickets",
    )

    panels = [
        FieldPanel("title_suffix"),
    ]
