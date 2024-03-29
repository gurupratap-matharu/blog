# Generated by Django 4.2.5 on 2023-09-06 23:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailcore", "0090_query_searchpromotion_querydailyhits"),
        ("locations", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CityIndexPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "intro",
                    models.TextField(blank=True, help_text="Text to describe the page"),
                ),
            ],
            options={
                "verbose_name": "City Index Page",
                "verbose_name_plural": "City Index Pages",
            },
            bases=("wagtailcore.page",),
        ),
    ]
