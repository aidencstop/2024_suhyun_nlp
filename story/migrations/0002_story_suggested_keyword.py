# Generated by Django 4.2.17 on 2025-03-01 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("story", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="story",
            name="suggested_keyword",
            field=models.TextField(blank=True, max_length=250, null=True),
        ),
    ]
