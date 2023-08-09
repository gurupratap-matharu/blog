from django.db import models

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    BaseSiteSetting,
    register_setting,
)
from wagtail.fields import StreamField
from wagtail.models import Page

from base.blocks import BaseStreamBlock
from modelcluster.models import ClusterableModel


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
