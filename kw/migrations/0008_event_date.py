# Generated by Django 4.0 on 2022-10-15 22:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kw', '0007_drop_issuer'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='date',
            field=models.DateField(default=datetime.date(2022, 1, 1), verbose_name='date'),
            preserve_default=False,
        ),
    ]
