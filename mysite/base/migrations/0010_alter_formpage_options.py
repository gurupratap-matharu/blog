# Generated by Django 5.0.6 on 2024-07-07 00:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0009_alter_country_options_alter_standardpage_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="formpage",
            options={"verbose_name": "formpage", "verbose_name_plural": "formpages"},
        ),
    ]
