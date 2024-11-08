# Generated by Django 5.1.2 on 2024-11-06 19:30

import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("partners", "0011_partnerpage_intro"),
    ]

    operations = [
        migrations.AddField(
            model_name="partnerpage",
            name="links",
            field=wagtail.fields.StreamField(
                [("Links", 4)],
                blank=True,
                block_lookup={
                    0: ("wagtail.blocks.CharBlock", (), {"required": True}),
                    1: ("wagtail.blocks.URLBlock", (), {"required": True}),
                    2: (
                        "wagtail.blocks.StructBlock",
                        [[("title", 0), ("link", 1)]],
                        {},
                    ),
                    3: ("wagtail.blocks.ListBlock", (2,), {}),
                    4: ("wagtail.blocks.StructBlock", [[("item", 3)]], {}),
                },
                verbose_name="Links Section",
            ),
        ),
    ]
