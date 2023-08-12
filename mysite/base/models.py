import logging
import pdb

from django.db import models
from django.forms import widgets

from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
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
from wagtail.models import Page

from base.blocks import BaseStreamBlock
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

logger = logging.getLogger(__name__)


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


class FormPage(AbstractEmailForm):
    page_description = "Use this page to create a simple form"

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = StreamField(BaseStreamBlock(), use_json_field=True)
    thank_you_text = RichTextField(blank=True)

    # Veer note how we include the FormField obj via an InlinePanel using the
    # related_name value
    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel("image"),
        FieldPanel("body"),
        InlinePanel("form_fields", heading="Form fields", label="Field"),
        FieldPanel("thank_you_text"),
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
