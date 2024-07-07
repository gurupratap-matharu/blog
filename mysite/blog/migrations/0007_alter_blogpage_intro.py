# Generated by Django 5.0.6 on 2024-07-07 00:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0006_alter_blogpage_body"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blogpage",
            name="intro",
            field=models.CharField(
                blank=True, help_text="Text to describe the page", max_length=500
            ),
        ),
    ]