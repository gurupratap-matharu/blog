# Generated by Django 4.2.3 on 2023-07-21 19:41

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0018_remove_docspage_cta_alter_docspage_body"),
        ("home", "0007_alter_calltoaction_id"),
    ]

    operations = [
        migrations.DeleteModel(
            name="CallToAction",
        ),
    ]
