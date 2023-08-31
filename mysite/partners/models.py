import logging

from django import forms
from django.db import models

from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.blocks import ListBlock
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from base.blocks import BaseStreamBlock, ImageBlock
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.models import ParentalKey, ParentalManyToManyField
from taggit.models import Tag, TaggedItemBase

logger = logging.getLogger(__name__)


class PartnerPageTag(TaggedItemBase):
    """
    This model allows us to create a many-to-many relationship between the PartnerPage and tags.

    For a longer guide on how to use it refer to
    https://docs.wagtail.org/en/stable/reference/pages/model_recipes.html#tagging

    """

    content_object = ParentalKey(
        "PartnerPage", related_name="tagged_items", on_delete=models.CASCADE
    )


class PartnerPage(Page):
    """
    A partner page to describe the details of a single partner.
    """

    page_description = "Use this to create a partner detail page"

    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    body = StreamField(
        BaseStreamBlock(), verbose_name="Page body", blank=True, use_json_field=True
    )

    tags = ClusterTaggableManager(through="partners.PartnerPageTag", blank=True)

    amenities = ParentalManyToManyField("partners.Amenity", blank=True)

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("logo"),
        FieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel("tags"),
                FieldPanel("amenities", widget=forms.CheckboxSelectMultiple),
            ],
            heading="Partner Information",
        ),
    ]
    # parent_page_types = ["partners.PartnerIndexPage"]
    # subpage_types = []

    class Meta:
        verbose_name = "partnerpage"
        verbose_name_plural = "partnerpages"


@register_snippet
class Amenity(models.Model):
    """
    An Amenity that a partner provides. Generally common across many partners and typically represented in a badge with an icon and optional text.
    """

    name = models.CharField(max_length=255)
    icon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("icon"),
    ]

    class Meta:
        verbose_name = "Amenity"
        verbose_name_plural = "Amenities"

    def __str__(self):
        return self.name
