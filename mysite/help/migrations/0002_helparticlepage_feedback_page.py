# Generated by Django 5.1.2 on 2024-12-10 01:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("help", "0001_initial"),
        ("wagtailcore", "0095_query_searchpromotion_querydailyhits"),
    ]

    operations = [
        migrations.AddField(
            model_name="helparticlepage",
            name="feedback_page",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailcore.page",
            ),
        ),
    ]
