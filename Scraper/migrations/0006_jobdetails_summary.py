# Generated by Django 4.2.23 on 2025-07-13 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Scraper', '0005_alter_source_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobdetails',
            name='summary',
            field=models.TextField(blank=True, null=True),
        ),
    ]
