# Generated by Django 5.0.4 on 2024-05-06 18:42

import django.core.validators
import django.db.models.deletion
import wagtail.blocks
import wagtail.embeds.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("locations", "0002_cityindexpage"),
        ("wagtailimages", "0026_delete_uploadedimage"),
    ]

    operations = [
        migrations.AddField(
            model_name="cityindexpage",
            name="image",
            field=models.ForeignKey(
                blank=True,
                help_text="Landscape model only; horizontal width between 1000px and 3000px.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
        migrations.AddField(
            model_name="citypage",
            name="image",
            field=models.ForeignKey(
                blank=True,
                help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
        migrations.AddField(
            model_name="citypage",
            name="intro",
            field=models.TextField(blank=True, help_text="Text to describe the page"),
        ),
        migrations.AddField(
            model_name="stationpage",
            name="address",
            field=models.TextField(default="Update this address please!"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="stationpage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    (
                        "heading_block",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "heading_text",
                                    wagtail.blocks.CharBlock(required=True),
                                ),
                                (
                                    "size",
                                    wagtail.blocks.ChoiceBlock(
                                        blank=True,
                                        choices=[
                                            ("", "Select a header size"),
                                            ("h2", "H2"),
                                            ("h3", "H3"),
                                            ("h4", "H4"),
                                        ],
                                        required=False,
                                    ),
                                ),
                            ]
                        ),
                    ),
                    (
                        "paragraph_block",
                        wagtail.blocks.RichTextBlock(
                            icon="pilcrow", template="blocks/paragraph_block.html"
                        ),
                    ),
                    (
                        "image_block",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "image",
                                    wagtail.images.blocks.ImageChooserBlock(
                                        required=True
                                    ),
                                ),
                                ("caption", wagtail.blocks.CharBlock(required=False)),
                                (
                                    "attribution",
                                    wagtail.blocks.CharBlock(required=False),
                                ),
                            ]
                        ),
                    ),
                    (
                        "gallery",
                        wagtail.blocks.ListBlock(
                            wagtail.blocks.StructBlock(
                                [
                                    (
                                        "image",
                                        wagtail.images.blocks.ImageChooserBlock(
                                            required=True
                                        ),
                                    ),
                                    (
                                        "caption",
                                        wagtail.blocks.CharBlock(required=False),
                                    ),
                                    (
                                        "attribution",
                                        wagtail.blocks.CharBlock(required=False),
                                    ),
                                ]
                            ),
                            template="blocks/gallery_block.html",
                        ),
                    ),
                    (
                        "block_quote",
                        wagtail.blocks.StructBlock(
                            [
                                ("text", wagtail.blocks.TextBlock()),
                                (
                                    "attribute_name",
                                    wagtail.blocks.CharBlock(
                                        blank=True,
                                        label="e.g. Mary Berry",
                                        required=False,
                                    ),
                                ),
                            ]
                        ),
                    ),
                    (
                        "embed_block",
                        wagtail.embeds.blocks.EmbedBlock(
                            help_text="Insert an embed URL e.g https://www.youtube.com/watch?v=SGJFWirQ3ks",
                            icon="media",
                            template="blocks/embed_block.html",
                        ),
                    ),
                    (
                        "faq",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "item",
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.StructBlock(
                                            [
                                                (
                                                    "question",
                                                    wagtail.blocks.CharBlock(
                                                        required=True
                                                    ),
                                                ),
                                                (
                                                    "answer",
                                                    wagtail.blocks.TextBlock(
                                                        required=True
                                                    ),
                                                ),
                                            ]
                                        )
                                    ),
                                )
                            ]
                        ),
                    ),
                ],
                blank=True,
                verbose_name="Page body",
            ),
        ),
        migrations.AddField(
            model_name="stationpage",
            name="image",
            field=models.ForeignKey(
                blank=True,
                help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
        migrations.AddField(
            model_name="stationpage",
            name="intro",
            field=models.TextField(blank=True, help_text="Text to describe the page"),
        ),
        migrations.AddField(
            model_name="stationpage",
            name="lat_long",
            field=models.CharField(
                default="21.0418,75.7876",
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
            preserve_default=False,
        ),
    ]
