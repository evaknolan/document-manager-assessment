# Generated by Django 4.1.9 on 2023-11-20 17:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("file_versions", "0007_alter_fileversion_version_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="fileversion",
            name="user",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
