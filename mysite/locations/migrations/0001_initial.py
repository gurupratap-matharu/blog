# Generated by Django 5.2 on 2025-05-04 22:09

import django.core.validators
import django.db.models.deletion
import wagtail.contrib.routable_page.models
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("base", "0001_initial"),
        ("wagtailcore", "0094_alter_page_locale"),
        ("wagtailimages", "0027_image_description"),
    ]

    operations = [
        migrations.CreateModel(
            name="CityIndexPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("social_text", models.CharField(blank=True, max_length=255)),
                (
                    "listing_title",
                    models.CharField(
                        blank=True,
                        help_text="Override the page title when this page appears on listings",
                        max_length=255,
                    ),
                ),
                (
                    "listing_summary",
                    models.CharField(
                        blank=True,
                        help_text="The text description used when this page appears on listings. It's also used if meta description is absent",
                        max_length=255,
                    ),
                ),
                (
                    "appear_in_search_results",
                    models.BooleanField(
                        default=True,
                        help_text="Make this page indexable by search engines.If unchecked this page will no longer be indexed by search engines.",
                    ),
                ),
                (
                    "intro",
                    models.TextField(blank=True, help_text="Text to describe the page"),
                ),
                (
                    "image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Landscape model only; horizontal width between 1000px and 3000px.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
                (
                    "listing_image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Choose an image you wish to be displayed when this page appears on listings",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
                (
                    "social_image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Choose an image you wish to display when this page appears on social media",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
            ],
            options={
                "verbose_name": "City Index Page",
                "verbose_name_plural": "City Index Pages",
            },
            bases=("wagtailcore.page", models.Model),
        ),
        migrations.CreateModel(
            name="CityPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("social_text", models.CharField(blank=True, max_length=255)),
                (
                    "listing_title",
                    models.CharField(
                        blank=True,
                        help_text="Override the page title when this page appears on listings",
                        max_length=255,
                    ),
                ),
                (
                    "listing_summary",
                    models.CharField(
                        blank=True,
                        help_text="The text description used when this page appears on listings. It's also used if meta description is absent",
                        max_length=255,
                    ),
                ),
                (
                    "appear_in_search_results",
                    models.BooleanField(
                        default=True,
                        help_text="Make this page indexable by search engines.If unchecked this page will no longer be indexed by search engines.",
                    ),
                ),
                (
                    "intro",
                    models.TextField(blank=True, help_text="Text to describe the page"),
                ),
                (
                    "lat_long",
                    models.CharField(
                        blank=True,
                        help_text="Comma separated lat/long. (Ex. 64.144367, -21.939182)                    Right click Google Maps and select 'What's Here'",
                        max_length=36,
                        validators=[
                            django.core.validators.RegexValidator(
                                code="invalid_lat_long",
                                message="Lat Long must be a comma-separated numeric lat and long",
                                regex="^(\\-?\\d+(\\.\\d+)?),\\s*(\\-?\\d+(\\.\\d+)?)$",
                            )
                        ],
                    ),
                ),
                (
                    "body",
                    wagtail.fields.StreamField(
                        [
                            ("heading_block", 2),
                            ("paragraph_block", 3),
                            ("image_block", 6),
                            ("gallery", 7),
                            ("block_quote", 10),
                            ("embed_block", 11),
                            ("faq", 16),
                            ("document", 17),
                            ("link", 24),
                            ("further_reading", 24),
                            ("nav_tab", 28),
                        ],
                        blank=True,
                        block_lookup={
                            0: ("wagtail.blocks.CharBlock", (), {"required": True}),
                            1: (
                                "wagtail.blocks.ChoiceBlock",
                                [],
                                {
                                    "blank": True,
                                    "choices": [
                                        ("", "Select a header size"),
                                        ("h2", "H2"),
                                        ("h3", "H3"),
                                        ("h4", "H4"),
                                    ],
                                    "required": False,
                                },
                            ),
                            2: (
                                "wagtail.blocks.StructBlock",
                                [[("heading_text", 0), ("size", 1)]],
                                {},
                            ),
                            3: (
                                "wagtail.blocks.RichTextBlock",
                                (),
                                {
                                    "icon": "pilcrow",
                                    "template": "blocks/paragraph_block.html",
                                },
                            ),
                            4: (
                                "wagtail.images.blocks.ImageChooserBlock",
                                (),
                                {"required": True},
                            ),
                            5: ("wagtail.blocks.CharBlock", (), {"required": False}),
                            6: (
                                "wagtail.blocks.StructBlock",
                                [[("image", 4), ("caption", 5), ("attribution", 5)]],
                                {},
                            ),
                            7: (
                                "wagtail.blocks.ListBlock",
                                (6,),
                                {"template": "blocks/gallery_block.html"},
                            ),
                            8: ("wagtail.blocks.TextBlock", (), {}),
                            9: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {
                                    "blank": True,
                                    "label": "e.g. Mary Berry",
                                    "required": False,
                                },
                            ),
                            10: (
                                "wagtail.blocks.StructBlock",
                                [[("text", 8), ("attribute_name", 9)]],
                                {},
                            ),
                            11: (
                                "wagtail.embeds.blocks.EmbedBlock",
                                (),
                                {
                                    "help_text": "Insert an embed URL e.g https://www.youtube.com/watch?v=SGJFWirQ3ks",
                                    "icon": "media",
                                    "template": "blocks/embed_block.html",
                                },
                            ),
                            12: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {"default": "Frequently asked questions"},
                            ),
                            13: (
                                "wagtail.blocks.RichTextBlock",
                                (),
                                {"required": True},
                            ),
                            14: (
                                "wagtail.blocks.StructBlock",
                                [[("question", 0), ("answer", 13)]],
                                {},
                            ),
                            15: ("wagtail.blocks.ListBlock", (14,), {}),
                            16: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 12), ("item", 15)]],
                                {},
                            ),
                            17: (
                                "wagtail.documents.blocks.DocumentChooserBlock",
                                (),
                                {"template": "blocks/document_block.html"},
                            ),
                            18: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {
                                    "help_text": "Leave blank to use page's listing title.",
                                    "required": False,
                                },
                            ),
                            19: ("wagtail.blocks.PageChooserBlock", (), {}),
                            20: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 18), ("page", 19)]],
                                {},
                            ),
                            21: ("wagtail.blocks.CharBlock", (), {}),
                            22: ("wagtail.blocks.URLBlock", (), {}),
                            23: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 21), ("link", 22)]],
                                {},
                            ),
                            24: (
                                "wagtail.blocks.StreamBlock",
                                [[("internal_link", 20), ("external_link", 23)]],
                                {},
                            ),
                            25: (
                                "wagtail.blocks.RichTextBlock",
                                (),
                                {
                                    "icon": "pilcrow",
                                    "required": True,
                                    "template": "blocks/paragraph_block.html",
                                },
                            ),
                            26: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 0), ("content", 25)]],
                                {},
                            ),
                            27: ("wagtail.blocks.ListBlock", (26,), {}),
                            28: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 0), ("item", 27)]],
                                {},
                            ),
                        },
                        verbose_name="Page body",
                    ),
                ),
                (
                    "faq",
                    wagtail.fields.StreamField(
                        [("faq", 5)],
                        blank=True,
                        block_lookup={
                            0: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {"default": "Frequently asked questions"},
                            ),
                            1: ("wagtail.blocks.CharBlock", (), {"required": True}),
                            2: ("wagtail.blocks.RichTextBlock", (), {"required": True}),
                            3: (
                                "wagtail.blocks.StructBlock",
                                [[("question", 1), ("answer", 2)]],
                                {},
                            ),
                            4: ("wagtail.blocks.ListBlock", (3,), {}),
                            5: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 0), ("item", 4)]],
                                {},
                            ),
                        },
                        verbose_name="FAQ Section",
                    ),
                ),
                (
                    "links",
                    wagtail.fields.StreamField(
                        [("Links", 7)],
                        blank=True,
                        block_lookup={
                            0: ("wagtail.blocks.CharBlock", (), {"required": True}),
                            1: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {
                                    "help_text": "Leave blank to use page's listing title.",
                                    "required": False,
                                },
                            ),
                            2: ("wagtail.blocks.PageChooserBlock", (), {}),
                            3: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 1), ("page", 2)]],
                                {},
                            ),
                            4: ("wagtail.blocks.ListBlock", (3,), {}),
                            5: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 0), ("item", 4)]],
                                {},
                            ),
                            6: ("wagtail.blocks.ListBlock", (5,), {}),
                            7: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 0), ("item", 6)]],
                                {},
                            ),
                        },
                        verbose_name="Links Section",
                    ),
                ),
                (
                    "companies",
                    wagtail.fields.StreamField(
                        [("Links", 5)],
                        blank=True,
                        block_lookup={
                            0: ("wagtail.blocks.CharBlock", (), {"required": True}),
                            1: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {
                                    "help_text": "Leave blank to use page's listing title.",
                                    "required": False,
                                },
                            ),
                            2: ("wagtail.blocks.PageChooserBlock", (), {}),
                            3: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 1), ("page", 2)]],
                                {},
                            ),
                            4: ("wagtail.blocks.ListBlock", (3,), {}),
                            5: (
                                "wagtail.blocks.StructBlock",
                                [[("heading_text", 0), ("item", 4)]],
                                {},
                            ),
                        },
                        verbose_name="Companies Section",
                    ),
                ),
                (
                    "country",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="cities",
                        to="base.country",
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
                (
                    "listing_image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Choose an image you wish to be displayed when this page appears on listings",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
                (
                    "social_image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Choose an image you wish to display when this page appears on social media",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
            ],
            options={
                "verbose_name": "City Page",
                "verbose_name_plural": "City Pages",
            },
            bases=("wagtailcore.page", models.Model),
        ),
        migrations.CreateModel(
            name="StationPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("social_text", models.CharField(blank=True, max_length=255)),
                (
                    "listing_title",
                    models.CharField(
                        blank=True,
                        help_text="Override the page title when this page appears on listings",
                        max_length=255,
                    ),
                ),
                (
                    "listing_summary",
                    models.CharField(
                        blank=True,
                        help_text="The text description used when this page appears on listings. It's also used if meta description is absent",
                        max_length=255,
                    ),
                ),
                (
                    "appear_in_search_results",
                    models.BooleanField(
                        default=True,
                        help_text="Make this page indexable by search engines.If unchecked this page will no longer be indexed by search engines.",
                    ),
                ),
                (
                    "intro",
                    models.TextField(blank=True, help_text="Text to describe the page"),
                ),
                (
                    "body",
                    wagtail.fields.StreamField(
                        [
                            ("heading_block", 2),
                            ("paragraph_block", 3),
                            ("image_block", 6),
                            ("gallery", 7),
                            ("block_quote", 10),
                            ("embed_block", 11),
                            ("faq", 16),
                            ("document", 17),
                            ("link", 24),
                            ("further_reading", 24),
                            ("nav_tab", 28),
                        ],
                        blank=True,
                        block_lookup={
                            0: ("wagtail.blocks.CharBlock", (), {"required": True}),
                            1: (
                                "wagtail.blocks.ChoiceBlock",
                                [],
                                {
                                    "blank": True,
                                    "choices": [
                                        ("", "Select a header size"),
                                        ("h2", "H2"),
                                        ("h3", "H3"),
                                        ("h4", "H4"),
                                    ],
                                    "required": False,
                                },
                            ),
                            2: (
                                "wagtail.blocks.StructBlock",
                                [[("heading_text", 0), ("size", 1)]],
                                {},
                            ),
                            3: (
                                "wagtail.blocks.RichTextBlock",
                                (),
                                {
                                    "icon": "pilcrow",
                                    "template": "blocks/paragraph_block.html",
                                },
                            ),
                            4: (
                                "wagtail.images.blocks.ImageChooserBlock",
                                (),
                                {"required": True},
                            ),
                            5: ("wagtail.blocks.CharBlock", (), {"required": False}),
                            6: (
                                "wagtail.blocks.StructBlock",
                                [[("image", 4), ("caption", 5), ("attribution", 5)]],
                                {},
                            ),
                            7: (
                                "wagtail.blocks.ListBlock",
                                (6,),
                                {"template": "blocks/gallery_block.html"},
                            ),
                            8: ("wagtail.blocks.TextBlock", (), {}),
                            9: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {
                                    "blank": True,
                                    "label": "e.g. Mary Berry",
                                    "required": False,
                                },
                            ),
                            10: (
                                "wagtail.blocks.StructBlock",
                                [[("text", 8), ("attribute_name", 9)]],
                                {},
                            ),
                            11: (
                                "wagtail.embeds.blocks.EmbedBlock",
                                (),
                                {
                                    "help_text": "Insert an embed URL e.g https://www.youtube.com/watch?v=SGJFWirQ3ks",
                                    "icon": "media",
                                    "template": "blocks/embed_block.html",
                                },
                            ),
                            12: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {"default": "Frequently asked questions"},
                            ),
                            13: (
                                "wagtail.blocks.RichTextBlock",
                                (),
                                {"required": True},
                            ),
                            14: (
                                "wagtail.blocks.StructBlock",
                                [[("question", 0), ("answer", 13)]],
                                {},
                            ),
                            15: ("wagtail.blocks.ListBlock", (14,), {}),
                            16: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 12), ("item", 15)]],
                                {},
                            ),
                            17: (
                                "wagtail.documents.blocks.DocumentChooserBlock",
                                (),
                                {"template": "blocks/document_block.html"},
                            ),
                            18: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {
                                    "help_text": "Leave blank to use page's listing title.",
                                    "required": False,
                                },
                            ),
                            19: ("wagtail.blocks.PageChooserBlock", (), {}),
                            20: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 18), ("page", 19)]],
                                {},
                            ),
                            21: ("wagtail.blocks.CharBlock", (), {}),
                            22: ("wagtail.blocks.URLBlock", (), {}),
                            23: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 21), ("link", 22)]],
                                {},
                            ),
                            24: (
                                "wagtail.blocks.StreamBlock",
                                [[("internal_link", 20), ("external_link", 23)]],
                                {},
                            ),
                            25: (
                                "wagtail.blocks.RichTextBlock",
                                (),
                                {
                                    "icon": "pilcrow",
                                    "required": True,
                                    "template": "blocks/paragraph_block.html",
                                },
                            ),
                            26: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 0), ("content", 25)]],
                                {},
                            ),
                            27: ("wagtail.blocks.ListBlock", (26,), {}),
                            28: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 0), ("item", 27)]],
                                {},
                            ),
                        },
                        verbose_name="Page body",
                    ),
                ),
                ("address", models.TextField()),
                (
                    "lat_long",
                    models.CharField(
                        help_text="Comma separated lat/long. (Ex. 64.144367, -21.939182)                    Right click Google Maps and select 'What's Here'",
                        max_length=36,
                        validators=[
                            django.core.validators.RegexValidator(
                                code="invalid_lat_long",
                                message="Lat Long must be a comma-separated numeric lat and long",
                                regex="^(\\-?\\d+(\\.\\d+)?),\\s*(\\-?\\d+(\\.\\d+)?)$",
                            )
                        ],
                    ),
                ),
                (
                    "faq",
                    wagtail.fields.StreamField(
                        [("faq", 5)],
                        blank=True,
                        block_lookup={
                            0: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {"default": "Frequently asked questions"},
                            ),
                            1: ("wagtail.blocks.CharBlock", (), {"required": True}),
                            2: ("wagtail.blocks.RichTextBlock", (), {"required": True}),
                            3: (
                                "wagtail.blocks.StructBlock",
                                [[("question", 1), ("answer", 2)]],
                                {},
                            ),
                            4: ("wagtail.blocks.ListBlock", (3,), {}),
                            5: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 0), ("item", 4)]],
                                {},
                            ),
                        },
                        verbose_name="FAQ Section",
                    ),
                ),
                (
                    "links",
                    wagtail.fields.StreamField(
                        [("Links", 5)],
                        blank=True,
                        block_lookup={
                            0: ("wagtail.blocks.CharBlock", (), {"required": True}),
                            1: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {
                                    "help_text": "Leave blank to use page's listing title.",
                                    "required": False,
                                },
                            ),
                            2: ("wagtail.blocks.PageChooserBlock", (), {}),
                            3: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 1), ("page", 2)]],
                                {},
                            ),
                            4: ("wagtail.blocks.ListBlock", (3,), {}),
                            5: (
                                "wagtail.blocks.StructBlock",
                                [[("heading_text", 0), ("item", 4)]],
                                {},
                            ),
                        },
                        verbose_name="Links Section",
                    ),
                ),
                (
                    "companies",
                    wagtail.fields.StreamField(
                        [("Links", 5)],
                        blank=True,
                        block_lookup={
                            0: ("wagtail.blocks.CharBlock", (), {"required": True}),
                            1: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {
                                    "help_text": "Leave blank to use page's listing title.",
                                    "required": False,
                                },
                            ),
                            2: ("wagtail.blocks.PageChooserBlock", (), {}),
                            3: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 1), ("page", 2)]],
                                {},
                            ),
                            4: ("wagtail.blocks.ListBlock", (3,), {}),
                            5: (
                                "wagtail.blocks.StructBlock",
                                [[("heading_text", 0), ("item", 4)]],
                                {},
                            ),
                        },
                        verbose_name="Companies Section",
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
                (
                    "listing_image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Choose an image you wish to be displayed when this page appears on listings",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
                (
                    "social_image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Choose an image you wish to display when this page appears on social media",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
            ],
            options={
                "verbose_name": "Station Page",
                "verbose_name_plural": "Station Pages",
            },
            bases=(
                wagtail.contrib.routable_page.models.RoutablePageMixin,
                "wagtailcore.page",
                models.Model,
            ),
        ),
    ]
