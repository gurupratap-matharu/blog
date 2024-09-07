# Generated by Django 5.0.8 on 2024-09-07 19:25

import django.core.validators
import django.db.models.deletion
import wagtail.contrib.routable_page.models
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("base", "0011_alter_footertext_locale_and_more"),
        ("wagtailcore", "0095_query_searchpromotion_querydailyhits"),
        ("wagtailimages", "0026_delete_uploadedimage"),
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
            ],
            options={
                "verbose_name": "City Index Page",
                "verbose_name_plural": "City Index Pages",
            },
            bases=("wagtailcore.page",),
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
                (
                    "intro",
                    models.TextField(blank=True, help_text="Text to describe the page"),
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
            ],
            options={
                "verbose_name": "City Page",
                "verbose_name_plural": "City Pages",
            },
            bases=("wagtailcore.page",),
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
                            ("faq", 15),
                            ("document", 16),
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
                            12: ("wagtail.blocks.TextBlock", (), {"required": True}),
                            13: (
                                "wagtail.blocks.StructBlock",
                                [[("question", 0), ("answer", 12)]],
                                {},
                            ),
                            14: ("wagtail.blocks.ListBlock", (13,), {}),
                            15: ("wagtail.blocks.StructBlock", [[("item", 14)]], {}),
                            16: (
                                "wagtail.documents.blocks.DocumentChooserBlock",
                                (),
                                {"template": "blocks/document_block.html"},
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
            ],
            options={
                "verbose_name": "Station Page",
                "verbose_name_plural": "Station Pages",
            },
            bases=(
                wagtail.contrib.routable_page.models.RoutablePageMixin,
                "wagtailcore.page",
            ),
        ),
    ]
