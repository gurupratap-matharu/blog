import json
import logging

from django import forms
from django.db import models
from django.utils.html import mark_safe

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.search import index

from base.blocks import (
    BaseStreamBlock,
    ContactBlock,
    FAQBlock,
    ImageLinkBlock,
    LinkBlock,
    NavTabBlock,
    NavTabLinksBlock,
    RatingsBlock,
)
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

        partners = self.get_children().live().order_by("-first_published_at")
        context["partners"] = partners

        return context

    def ld_entity(self):

        page_schema = json.dumps(
            {
                "@context": "http://schema.org",
                "@graph": [
                    self._get_breadcrumb_schema(),
                    self._get_image_schema(),
                    self._get_article_schema(),
                    self._get_organisation_schema(),
                    self._get_faq_schema(),
                ],
            },
            ensure_ascii=False,
        )
        return mark_safe(page_schema)

    def _get_breadcrumb_schema(self):

        breadcrumb_schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Argentina",
                    "item": "https://ventanita.com.ar/",
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Empresas de Micro",
                    "item": "https://ventanita.com.ar/empresas-de-bus/",
                },
            ],
        }
        return breadcrumb_schema


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

    intro = models.TextField(
        help_text="A brief introduction about the company", blank=True
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

    destinations = StreamField(
        [("destinations", ImageLinkBlock())],
        verbose_name="Destinations where this operator has presence",
        blank=True,
        max_num=1,
        use_json_field=True,
    )

    info = StreamField(
        [("Info", NavTabBlock())],
        verbose_name="Info Section",
        blank=True,
        max_num=1,
        use_json_field=True,
    )

    routes = StreamField(
        [("Routes", NavTabLinksBlock())],
        verbose_name="Routes Section",
        blank=True,
        max_num=1,
        use_json_field=True,
    )

    faq = StreamField(
        [("faq", FAQBlock())],
        verbose_name="FAQ Section",
        blank=True,
        max_num=1,
        use_json_field=True,
    )

    links = StreamField(
        [("Links", LinkBlock())],
        verbose_name="Links Section",
        blank=True,
        max_num=1,
        use_json_field=True,
    )

    ratings = StreamField(
        [("Ratings", RatingsBlock())],
        verbose_name="Ratings",
        blank=True,
        max_num=1,
        collapsed=True,
    )

    search_fields = BasePage.search_fields + [
        index.SearchField("body"),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel("logo"),
        FieldPanel("intro"),
        FieldPanel("hero_image"),
        FieldPanel("info"),
        FieldPanel("contact"),
        FieldPanel("body"),
        FieldPanel("destinations"),
        FieldPanel("routes"),
        FieldPanel("faq"),
        FieldPanel("links"),
        FieldPanel("ratings"),
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

    def ld_entity(self):

        page_schema = json.dumps(
            {
                "@context": "http://schema.org",
                "@graph": [
                    self._get_breadcrumb_schema(),
                    self._get_image_schema(),
                    self._get_article_schema(),
                    self._get_organisation_schema(),
                    self._get_faq_schema(),
                ],
            },
            ensure_ascii=False,
        )
        return mark_safe(page_schema)

    def _get_organisation_schema(self):
        """
        This method is overwritten since operator landing pages should have details about the
        bus operator in the organisation schema markup with aggregated Ratings.
        """

        image = self.logo or self.listing_image or self.social_image
        image_url = image.file.url if image else ""

        if self.ratings:
            obj = self.ratings[0].value
            rating_value = str(obj.get_score())
            rating_count = str(obj.get_total_ratings())
        else:
            rating_value = rating_count = 0

        org_schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": self.title,
            "url": self.full_url,
            "logo": f"https://ventanita.com.ar{image_url}",
            "image": f"https://ventanita.com.ar{image_url}",
            "description": self.search_description,
            "email": "support@ventanita.com.ar",
            "telephone": "+54-11-5025-4191",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Uspallata 471",
                "addressLocality": "Buenos Aires",
                "addressCountry": "AR",
                "addressRegion": "CABA",
                "postalCode": "1143",
            },
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": "+54-911-5025-4191",
                "email": "support@ventanita.com.ar",
            },
            "sameAs": [],
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": rating_value,
                "ratingCount": rating_count,
                "bestRating": "5",
                "worstRating": "1",
            },
        }

        return org_schema

    def _get_breadcrumb_schema(self):

        breadcrumb_schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Argentina",
                    "item": "https://ventanita.com.ar/",
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Empresas de Bus",
                    "item": self.get_parent().full_url,
                },
                {
                    "@type": "ListItem",
                    "position": 3,
                    "name": self.title,
                    "item": self.full_url,
                },
            ],
        }
        return breadcrumb_schema


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
