"""
On loading, Wagtail will search for any app with the file `wagtail_hooks.py`
and execute the contents. This provides a way to register our own functions to execute
at certain points in Wagtail’s execution, such as when a page is saved or when the
main menu is constructed.
"""

import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail import hooks
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    InlineStyleElementHandler,
)
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from locations.models import Service

from base.models import Country, FooterText, Person
from blog.models import BlogCategory
from partners.models import Amenity


class ServiceViewSet(SnippetViewSet):
    model = Service
    icon = "tag"


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
    items = (
        PersonViewSet,
        BlogCategoryViewSet,
        ServiceViewSet,
        FooterTextViewSet,
    )


register_snippet(MiscSnippetViewSetGroup)
register_snippet(PartnerViewSetGroup)


# Rich text features
@hooks.register("register_rich_text_features")
def register_mark_feature(features):
    """
    Registering the `mark` feature, which uses the `MARK` Draft.js inline style type, and is stored as HTML with a `<mark>` tag.
    """

    feature_name = "mark"
    type_ = "MARK"
    tag = "mark"

    # how draftail handles the features in its toolbar.
    control = {
        "type": type_,
        "description": "Mark",
        "icon": "info-circle",
    }

    # Call register_editor_plugin to register the configuration for draftail
    features.register_editor_plugin(
        "draftail", feature_name, draftail_features.InlineStyleFeature(control)
    )

    # Configure the content transform from DB to the editor and back
    db_conversion = {
        "from_database_format": {tag: InlineStyleElementHandler(type_)},
        "to_database_format": {"style_map": {type_: tag}},
    }

    # Register the converter
    features.register_converter_rule(
        "contentstate", feature_name, db_conversion
    )

    # Add feature to the default features list
    features.default_features.append("mark")


@hooks.register("register_rich_text_features")
def register_small_feature(features):
    """
    Registering the `small` feature, which uses the `SMALL` Draft.js inline style type
    and is stored as HTML with a `<small>` tag.
    """

    feature_name = "small"
    type_ = "SMALL"
    tag = "small"

    # how draftail handles the features in its toolbar.
    control = {
        "type": type_,
        "description": "small",
        "icon": "arrow-down",
    }

    # Call register_editor_plugin to register the configuration for draftail
    features.register_editor_plugin(
        "draftail", feature_name, draftail_features.InlineStyleFeature(control)
    )

    # Configure the content transform from DB to the editor and back
    db_conversion = {
        "from_database_format": {tag: InlineStyleElementHandler(type_)},
        "to_database_format": {"style_map": {type_: tag}},
    }

    # Register the converter
    features.register_converter_rule(
        "contentstate", feature_name, db_conversion
    )

    # Add feature to the default features list
    features.default_features.append("small")


@hooks.register("register_rich_text_features")
def register_underline_feature(features):
    """
    Registering the `underline` feature, which uses the `UNDERLINE` Draft.js inline style type.
    """

    feature_name = "underline"
    type_ = "UNDERLINE"
    tag = "u"

    control = {"type": type_, "description": "underline", "label": "⎁"}
    inline_feature = draftail_features.InlineStyleFeature(control)

    features.register_editor_plugin("draftail", feature_name, inline_feature)

    db_conversion = {
        "from_database_format": {tag: InlineStyleElementHandler(type_)},
        "to_database_format": {"style_map": {type_: tag}},
    }
    features.register_converter_rule(
        "contentstate", feature_name, db_conversion
    )
    features.default_features.append("underline")
