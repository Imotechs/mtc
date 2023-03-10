# Generated by Django 4.0.1 on 2023-02-17 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_remove_buytrade_usdt_remove_selltrade_usdt'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=150)),
                ('body', models.TextField()),
                ('date', models.DateTimeField(auto_now=True)),
                ('read', models.BooleanField(default=False)),
            ],
        ),
    ]
