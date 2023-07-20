# Generated by Django 4.2.3 on 2023-07-20 18:53

from django.db import migrations
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0012_alter_docspage_body"),
    ]

    operations = [
        migrations.AlterField(
            model_name="docspage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    ("heading", wagtail.blocks.CharBlock(form_classname="title")),
                    ("paragraph", wagtail.blocks.TextBlock()),
                    ("image", wagtail.images.blocks.ImageChooserBlock()),
                    (
                        "gallery",
                        wagtail.blocks.ListBlock(
                            wagtail.images.blocks.ImageChooserBlock()
                        ),
                    ),
                    ("link", wagtail.blocks.URLBlock()),
                    ("email", wagtail.blocks.EmailBlock()),
                    ("datetime", wagtail.blocks.DateTimeBlock()),
                    ("date", wagtail.blocks.DateBlock()),
                    ("time", wagtail.blocks.TimeBlock()),
                    ("boolean", wagtail.blocks.BooleanBlock()),
                    ("choices", wagtail.blocks.ChoiceBlock(choices=[])),
                    ("chooser", wagtail.blocks.ChooserBlock()),
                    ("html", wagtail.blocks.RawHTMLBlock()),
                    ("blockquote", wagtail.blocks.BlockQuoteBlock()),
                ],
                use_json_field=True,
            ),
        ),
    ]
