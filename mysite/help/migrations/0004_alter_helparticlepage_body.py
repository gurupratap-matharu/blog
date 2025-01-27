# Generated by Django 5.1.4 on 2025-01-13 20:05

import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("help", "0003_remove_helparticlepage_feedback_page"),
    ]

    operations = [
        migrations.AlterField(
            model_name="helparticlepage",
            name="body",
            field=wagtail.fields.StreamField(
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
                        {"icon": "pilcrow", "template": "blocks/paragraph_block.html"},
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
                        {"blank": True, "label": "e.g. Mary Berry", "required": False},
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
                    13: ("wagtail.blocks.TextBlock", (), {"required": True}),
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
                verbose_name="Page Body",
            ),
        ),
    ]
