# Generated by Django 4.0.1 on 2023-01-14 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_lockedasset'),
    ]

    operations = [
        migrations.AddField(
            model_name='lockedasset',
            name='profit',
            field=models.FloatField(default=0.0),
        ),
    ]