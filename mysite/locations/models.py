import logging

from django.core.validators import RegexValidator
from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.search import index

from base.blocks import BaseStreamBlock

logger = logging.getLogger(__name__)


class CityIndexPage(Page):
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

    content_panels = Page.content_panels + [
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


class CityPage(Page):
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
    country = models.ForeignKey(
        "base.Country",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="cities",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("image"),
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

        context = super().get_context(request, *args, **kwargs)
        context["stations"] = self.get_children().live().order_by("title")
        return context


class StationPage(RoutablePageMixin, Page):
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

    body = StreamField(
        BaseStreamBlock(), verbose_name="Page body", blank=True, use_json_field=True
    )
    address = models.TextField()
    lat_long = models.CharField(
        max_length=36,
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

    search_fields = Page.search_fields + [
        index.SearchField("address"),
        index.SearchField("body"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("image"),
        FieldPanel("body"),
        FieldPanel("address"),
        FieldPanel("lat_long"),
    ]

    parent_page_types = ["locations.CityPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Station Page"
        verbose_name_plural = "Station Pages"

    def __str__(self):
        return self.title

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["lat"] = self.lat_long.split(",")[0]
        context["long"] = self.lat_long.split(",")[1]

        return context
