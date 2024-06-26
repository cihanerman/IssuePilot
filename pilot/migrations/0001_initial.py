# Generated by Django 5.0.6 on 2024-05-16 16:09

from django.db import migrations, models

import pilot.enums


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Repository",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("owner", models.CharField(max_length=255)),
                (
                    "repository_type",
                    models.IntegerField(
                        choices=[(1, "GITHUB")],
                        default=pilot.enums.RepositoryTypes["GITHUB"],
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
    ]
