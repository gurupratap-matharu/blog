import logging

from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.models import Page

logger = logging.getLogger(__name__)


class CityIndexPage(Page):
    page_description = "Use this page to show a list of cities"

    intro = models.TextField(help_text="Text to describe the page", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["CityPage"]

    class Meta:
        verbose_name = "City Index Page"
        verbose_name_plural = "City Index Pages"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["cities"] = self.get_children().live().order_by("-first_published_at")
        return context


class CityPage(Page):
    page_description = "Use this page to create a city"

    country = models.ForeignKey(
        "base.Country",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="cities",
    )

    content_panels = Page.content_panels + [
        FieldPanel("country"),
    ]

    parent_page_types = ["locations.CityIndexPage"]
    subpage_types = ["locations.StationPage"]

    class Meta:
        verbose_name = "City Page"
        verbose_name_plural = "City Pages"


class StationPage(Page):
    """
    A station detail view which represent a stop | terminal | station
    This is a leaf page and the hierarchy is country -> city -> station
    """

    page_description = "Use this to create a station or terminal page"

    parent_page_types = ["locations.CityPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Station Page"
        verbose_name_plural = "Station Pages"
