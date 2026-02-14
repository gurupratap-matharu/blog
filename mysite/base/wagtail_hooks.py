"""
On loading, Wagtail will search for any app with the file `wagtail_hooks.py`
and execute the contents. This provides a way to register our own functions to execute
at certain points in Wagtail’s execution, such as when a page is saved or when the
main menu is constructed.
"""

from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from base.models import Country, FooterText, Person
from blog.models import BlogCategory
from partners.models import Amenity


class AmenityViewSet(SnippetViewSet):
    model = Amenity
    icon = "tag"
    search_fields = ("name",)


class CountryViewSet(SnippetViewSet):
    model = Country
    icon = "globe"
    search_fields = ("title",)


class PartnerViewSetGroup(SnippetViewSetGroup):
    menu_label = "Partners"
    menu_icon = "group"
    menu_order = 200
    items = (CountryViewSet, AmenityViewSet)


class PersonViewSet(SnippetViewSet):
    """
    Add the person model to snippets section.
    """

    model = Person
    icon = "group"
    list_display = ("first_name", "last_name", "job_title", "thumb_image")
    list_filter = {"job_title": ["icontains"]}


class FooterTextViewSet(SnippetViewSet):
    """
    Add the footer text model to snippets section.
    """

    model = FooterText
    icon = "doc-full"
    search_fields = ("body",)


class BlogCategoryViewSet(SnippetViewSet):
    model = BlogCategory
    icon = "tag"
    search_fields = ("name",)


class MiscSnippetViewSetGroup(SnippetViewSetGroup):
    menu_label = "Misc"
    menu_icon = "list-ul"
    menu_order = 300
    items = (PersonViewSet, BlogCategoryViewSet, FooterTextViewSet)


register_snippet(MiscSnippetViewSetGroup)
register_snippet(PartnerViewSetGroup)
