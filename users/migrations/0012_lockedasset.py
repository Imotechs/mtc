# Generated by Django 4.0.1 on 2023-01-13 18:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0011_profile_referred_bonus'),
    ]

    operations = [
        migrations.CreateModel(
            name='LockedAsset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('claimed', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now=True)),
                ('date_to', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
