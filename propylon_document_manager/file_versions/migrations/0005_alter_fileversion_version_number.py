# Generated by Django 4.1.9 on 2023-11-20 15:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("file_versions", "0004_alter_fileversion_url_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fileversion",
            name="version_number",
            field=models.IntegerField(blank=True, default=1, editable=False),
        ),
    ]
