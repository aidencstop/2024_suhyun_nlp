# Generated by Django 4.2.17 on 2025-03-14 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("story", "0004_story_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="genre",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]
