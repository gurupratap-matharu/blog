import logging

from django import forms
from django.core.paginator import Paginator
from django.db import models

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from base.blocks import BaseStreamBlock
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.models import ParentalKey, ParentalManyToManyField
from taggit.models import TaggedItemBase

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


class PartnerIndexPage(Page):
    page_description = "Use this page to show a list of partners"

    intro = models.TextField(help_text="Text to describe the page", blank=True)

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px to 3000px.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("image"),
    ]

    # Specify that only blog pages can be children of this blogindex page
    subpage_types = ["PartnerPage"]

    class Meta:
        verbose_name = "partnerindexpage"
        verbose_name_plural = "partnerindexpages"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        qs = (
            self.get_children().live().order_by("-first_published_at")
        )  # <-- change this to by country

        paginator = Paginator(qs, 9)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context["partners"] = context["page_obj"] = page_obj

        return context


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
    parent_page_types = ["partners.PartnerIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "partnerpage"
        verbose_name_plural = "partnerpages"

    def get_tags(self):
        """
        Find all the tags that are related to the blog post into a list we can access on the template.
        We're additionally adding a URL to access BlogPage objects with that tag
        """

        base_url = self.get_parent().url
        tags = self.tags.all()

        for tag in tags:
            tag.url = f"{base_url}tags/{tag.slug}/"

        return tags


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
