import json
import logging
from datetime import time

from django import forms
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.contrib.routable_page.models import RoutablePageMixin
from wagtail.fields import StreamField
from wagtail.models import Orderable
from wagtail.search import index

from modelcluster.fields import ParentalKey, ParentalManyToManyField

from base.blocks import (
    BaseStreamBlock,
    FAQBlock,
    LinkBlock,
    NavTabLinksBlock,
    RatingsBlock,
)
from base.choices import Country, Province, Weekday
from base.models import BasePage
from base.validators import validate_lat_lng, validate_phone


logger = logging.getLogger(__name__)


class CityIndexPage(BasePage):
    """
    A Page model that creates an index page (a listview)
    """

    page_description = "Use this page to show a list of cities"

    intro = models.TextField(help_text="Text to describe the page", blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape model only; horizontal width between 1000px and 3000px.",
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
        FieldPanel("image"),
    ]

    subpage_types = ["CityPage"]

    class Meta:
        verbose_name = "City Index Page"
        verbose_name_plural = "City Index Pages"

    def children(self):
        """
        Allow children of this indexpage to be accessible via the indexpage object on
        templates. We can use this to show featured sections of the site and their
        child pages.
        """
        return self.get_children().specific().live()

    def get_context(self, request, *args, **kwargs):
        """
        Overrides the context to list all child items, that are live, by title
        alphabetical order.
        """

        context = super().get_context(request, *args, **kwargs)
        context["cities"] = self.get_children().live().order_by("title")
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
                    "name": "Terminales",
                    "item": "https://ventanita.com.ar/pasajes-de-micro/",
                },
            ],
        }

        return breadcrumb_schema


class CityPage(BasePage):
    """
    Detail page for a specific city or town.
    """

    page_description = "Use this page to create a city"

    intro = models.TextField(help_text="Text to describe the page", blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )

    lat_long = models.CharField(
        max_length=36,
        blank=True,
        help_text="Comma separated lat/long. (Ex. 64.144367, -21.939182) \
                   Right click Google Maps and select 'What's Here'",
        validators=[
            RegexValidator(
                regex=r"^(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)$",
                message="Lat Long must be a comma-separated numeric lat and long",
                code="invalid_lat_long",
            ),
        ],
    )

    body = StreamField(
        BaseStreamBlock(), verbose_name="Page body", blank=True, collapsed=True
    )

    faq = StreamField(
        [("faq", FAQBlock())],
        verbose_name="FAQ Section",
        blank=True,
        max_num=1,
        collapsed=True,
    )

    links = StreamField(
        [("Links", NavTabLinksBlock())],
        verbose_name="Links Section",
        blank=True,
        max_num=1,
        collapsed=True,
    )

    companies = StreamField(
        [("Links", LinkBlock())],
        verbose_name="Companies Section",
        blank=True,
        max_num=1,
        collapsed=True,
    )

    country = models.ForeignKey(
        "base.Country",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="cities",
    )

    search_fields = BasePage.search_fields + [index.SearchField("body")]

    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
        FieldPanel("image"),
        FieldPanel("lat_long"),
        FieldPanel("body"),
        FieldPanel("faq"),
        FieldPanel("links"),
        FieldPanel("companies"),
        FieldPanel("country"),
    ]

    parent_page_types = ["locations.CityIndexPage"]
    subpage_types = ["locations.StationPage"]

    class Meta:
        verbose_name = "City Page"
        verbose_name_plural = "City Pages"

    def __str__(self):
        return self.title

    def get_context(self, request, *args, **kwargs):
        """
        Overrides the context to list all child items, that are live, by title
        alphabetical order.
        """

        lat_long = self.lat_long or ","
        lat, long = lat_long.split(",")

        context = super().get_context(request, *args, **kwargs)
        context["lat_long"] = {"lat": lat, "long": long}
        context["stations"] = self.get_children().live().order_by("title")

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
                    "name": "Pasajes de Micro",
                    "item": "https://ventanita.com.ar/",
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Argentina",
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


class StationIndexPage(BasePage):
    page_description = "Use this page to show a list of terminals or stations"
    intro = models.TextField(help_text="Text to describe the page", blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )
    body = StreamField(
        BaseStreamBlock(), verbose_name="Page body", blank=True, collapsed=True
    )
    faq = StreamField(
        [("faq", FAQBlock())],
        verbose_name="FAQ Section",
        blank=True,
        max_num=1,
        collapsed=True,
    )
    links = StreamField(
        [("Links", LinkBlock())],
        verbose_name="Links Section",
        blank=True,
        max_num=1,
        collapsed=True,
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("intro", classname="collapsed"),
        FieldPanel("image", classname="collapsed"),
        FieldPanel("body", classname="collapsed"),
        FieldPanel("faq", classname="collapsed"),
        FieldPanel("links", classname="collapsed"),
    ]

    class Meta:
        verbose_name = "Station Index Page"
        verbose_name_plural = "Station Index Pages"

    def children(self):
        return self.get_children().specific().live()

    def ld_entity(self):
        page_schema = json.dumps(
            {
                "@context": "http://schema.org",
                "@graph": [
                    self._get_breadcrumb_schema(),
                    self._get_image_schema(),
                    self._get_faq_schema(),
                    self._get_article_schema(),
                    self._get_organisation_schema(),
                ],
            },
            ensure_ascii=False,
        )
        return mark_safe(page_schema)

    def _get_breadcrumb_schema(self):
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Inicio",
                    "item": "https://ventanita.com.ar/",
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Terminales De Micro",
                    "item": self.full_url,
                },
            ],
        }


class StationPage(RoutablePageMixin, BasePage):
    """
    A station detail view which represent a stop | terminal | station
    This is a leaf page and the hierarchy is country -> city -> station
    """

    page_description = "Use this to create a station or terminal page"

    intro = models.TextField(help_text="Text to describe the page", blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )
    lat_long = models.CharField(
        max_length=36,
        help_text="Comma separated lat/long. (Ex. 64.144367, -21.939182) \
                   Right click Google Maps and select 'What's Here'",
        validators=[validate_lat_lng],
    )
    address = models.TextField(_("address"), blank=True)
    phone = models.CharField(
        _("Phone"), max_length=20, blank=True, validators=[validate_phone]
    )
    province = models.CharField(
        _("Province"), max_length=20, choices=Province, blank=True
    )
    province_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="terminales",
    )
    country = models.CharField(
        _("Country"), max_length=20, choices=Country, blank=True
    )
    services = ParentalManyToManyField("locations.Service", blank=True)
    directions = StreamField(
        BaseStreamBlock(),
        verbose_name="Directions (Como llegar?)",
        blank=True,
        collapsed=True,
    )

    body = StreamField(
        BaseStreamBlock(), verbose_name="Page body", blank=True, collapsed=True
    )

    faq = StreamField(
        [("faq", FAQBlock())],
        verbose_name="FAQ Section",
        blank=True,
        max_num=1,
        collapsed=True,
    )

    links = StreamField(
        [("Links", LinkBlock())],
        verbose_name="Links Section",
        blank=True,
        max_num=1,
        collapsed=True,
    )

    companies = StreamField(
        [("Links", LinkBlock())],
        verbose_name="Companies Section",
        blank=True,
        max_num=1,
        collapsed=True,
    )
    ratings = StreamField(
        [("Ratings", RatingsBlock())],
        verbose_name="Ratings",
        blank=True,
        max_num=1,
        collapsed=True,
    )

    search_fields = BasePage.search_fields + [
        index.SearchField("address"),
        index.SearchField("body"),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
        MultiFieldPanel(
            [
                FieldPanel("phone"),
                FieldPanel("address"),
                FieldPanel("lat_long"),
                FieldPanel("province"),
                PageChooserPanel("province_page"),
                FieldPanel("country"),
                FieldPanel("services", widget=forms.CheckboxSelectMultiple),
                InlinePanel(
                    "opening_hours",
                    label="Opening Hours",
                    classname="collapsed",
                    max_num=7,
                ),
            ],
            heading="Basic Info",
            classname="collapsed",
        ),
        FieldPanel("directions", classname="collapsed"),
        FieldPanel("body", classname="collapsed"),
        FieldPanel("faq", classname="collapsed"),
        FieldPanel("links", classname="collapsed"),
        FieldPanel("companies", classname="collapsed"),
        FieldPanel("ratings", classname="collapsed"),
        MultiFieldPanel(
            [
                FieldPanel("image"),
                InlinePanel("gallery_images", label="Gallery"),
            ],
            heading="Media",
            classname="collapsed",
        ),
    ]

    class Meta:
        verbose_name = "Station Page"
        verbose_name_plural = "Station Pages"

    def __str__(self):
        return self.title

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        lat, long = self.lat_long.split(",")
        options = {
            "lat": lat,
            "long": long,
            "title": self.title,
            "text": self.intro,
            "url": self.get_full_url(),
        }
        context["options"] = options
        context["today"] = timezone.now().weekday()
        return context

    def get_google_maps_directions_url(self):
        return f"https://www.google.com/maps/dir/?api=1&destination={self.lat_long}"

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
            }
        )
        return mark_safe(page_schema)

    def _get_breadcrumb_schema(self):
        return {
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
                    "name": "Terminales",
                    "item": self.get_parent().get_parent().full_url,
                },
                {
                    "@type": "ListItem",
                    "position": 3,
                    "name": self.get_parent().title,
                    "item": self.get_parent().full_url,
                },
                {
                    "@type": "ListItem",
                    "position": 4,
                    "name": self.title,
                    "item": self.full_url,
                },
            ],
        }


class StationPageGalleryImage(Orderable):
    page = ParentalKey(
        "StationPage", on_delete=models.CASCADE, related_name="gallery_images"
    )
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+"
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = ["image", "caption"]

    class Meta:
        verbose_name = "stationpagegallery"
        verbose_name_plural = "stationpagegallery"


def default_open_time():
    return time(hour=7)


def default_close_time():
    return time(hour=23)


class OpeningHour(Orderable):
    page = ParentalKey(
        "locations.StationPage",
        on_delete=models.CASCADE,
        related_name="opening_hours",
    )
    weekday = models.PositiveIntegerField(_("weekday"), choices=Weekday)
    open_time = models.TimeField(_("start"), default=default_open_time)
    close_time = models.TimeField(_("end"), default=default_close_time)
    closed = models.BooleanField(_("closed"), default=False)
    panels = [
        FieldRowPanel(
            [
                FieldPanel("weekday"),
                FieldPanel("open_time"),
                FieldPanel("close_time"),
                FieldPanel("closed"),
            ]
        )
    ]

    class Meta:
        verbose_name = "openinghour"
        verbose_name_plural = "openinghours"

    def __str__(self):
        return (
            f"{self.get_weekday_display()} {self.open_time}:{self.close_time}"
        )


class Service(models.Model):
    """
    A service that a station or terminal provides.
    Typically represented in a badge with an icon and optional text for visual purposes
    eg: Washrooms, Cafeteria, Waiting Room, Lockers, etc
    """

    name = models.CharField(_("name"), max_length=255)
    icon = models.CharField(
        _("icon"), max_length=20, help_text="Only name of the icon"
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("icon"),
    ]

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.name
