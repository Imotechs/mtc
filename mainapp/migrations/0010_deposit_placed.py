# Generated by Django 4.0.1 on 2022-09-18 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0009_rename_option_deposit_method_deposit_transaction_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='deposit',
            name='placed',
            field=models.BooleanField(default=False),
        ),
    ]
