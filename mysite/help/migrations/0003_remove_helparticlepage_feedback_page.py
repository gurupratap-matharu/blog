# Generated by Django 5.1.2 on 2024-12-11 19:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("help", "0002_helparticlepage_feedback_page"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="helparticlepage",
            name="feedback_page",
        ),
    ]
