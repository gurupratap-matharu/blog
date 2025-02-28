# Generated by Django 5.1.2 on 2024-11-09 21:06

import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0004_citypage_body_citypage_faq_citypage_links"),
    ]

    operations = [
        migrations.AddField(
            model_name="citypage",
            name="companies",
            field=wagtail.fields.StreamField(
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
    ]
