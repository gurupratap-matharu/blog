# Generated by Django 4.2.4 on 2023-08-28 17:36

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0005_alter_blogpage_body"),
    ]

    operations = [
        migrations.DeleteModel(
            name="BlogTagIndexPage",
        ),
    ]
