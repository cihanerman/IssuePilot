# Generated by Django 5.0.6 on 2024-05-16 16:09

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pilot', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='users',
            field=models.ManyToManyField(related_name='repositories', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='repository',
            index=models.Index(fields=['name'], name='pilot_repos_name_080e37_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='repository',
            unique_together={('name', 'repository_type')},
        ),
    ]
