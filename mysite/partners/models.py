import logging

from django import forms
from django.core.paginator import Paginator
from django.db import models

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.search import index

from base.blocks import BaseStreamBlock, ContactBlock, FAQBlock
from base.models import BasePage
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


class PartnerIndexPage(BasePage):
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

    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
        FieldPanel("image"),
    ]

    subpage_types = ["PartnerPage"]

    class Meta:
        verbose_name = "partnerindexpage"
        verbose_name_plural = "partnerindexpages"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        qs = (
            self.get_children().live().order_by("-first_published_at")
        )  # <-- change this to by country

        paginator = Paginator(qs, 12)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context["partners"] = context["page_obj"] = page_obj

        return context


class PartnerPage(BasePage):
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

    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    contact = StreamField(
        [("contact", ContactBlock())],
        verbose_name="Contact Information",
        blank=True,
        max_num=1,
        use_json_field=True,
    )

    body = StreamField(
        BaseStreamBlock(), verbose_name="Page body", blank=True, use_json_field=True
    )

    tags = ClusterTaggableManager(through="partners.PartnerPageTag", blank=True)

    amenities = ParentalManyToManyField("partners.Amenity", blank=True)
    faq = StreamField(
        [("faq", FAQBlock())],
        verbose_name="FAQ Section",
        blank=True,
        max_num=1,
        use_json_field=True,
    )
    search_fields = BasePage.search_fields + [
        index.SearchField("body"),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel("logo"),
        FieldPanel("contact"),
        FieldPanel("body"),
        FieldPanel("faq"),
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
        Find all the tags that are related to the partner into a list we can access on the template.
        We're additionally adding a URL to access ParterPage objects with that tag
        """

        base_url = self.get_parent().url
        tags = self.tags.all()

        for tag in tags:
            tag.url = f"{base_url}tags/{tag.slug}/"

        return tags


class Amenity(models.Model):
    """
    An Amenity that a partner provides. Generally common across many partners and typically
    represented in a badge with an icon and optional text.
    """

    name = models.CharField(max_length=255)
    icon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    icon_name = models.CharField(
        max_length=20, help_text="Name of the bootstrap icon", blank=True, null=True
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("icon"),
        FieldPanel("icon_name"),
    ]

    class Meta:
        verbose_name = "Amenity"
        verbose_name_plural = "Amenities"

    def __str__(self):
        return self.name
