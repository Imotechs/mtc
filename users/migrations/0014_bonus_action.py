# Generated by Django 4.0.1 on 2023-01-14 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_lockedasset_profit'),
    ]

    operations = [
        migrations.AddField(
            model_name='bonus',
            name='action',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
