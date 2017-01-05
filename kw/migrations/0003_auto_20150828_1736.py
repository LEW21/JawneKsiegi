# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kw', '0002_views'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='private',
        ),
        migrations.AddField(
            model_name='account',
            name='address_public',
            field=models.BooleanField(default=False, verbose_name='publish address?'),
        ),
        migrations.AddField(
            model_name='account',
            name='bank_account_public',
            field=models.BooleanField(default=False, verbose_name='publish bank account?'),
        ),
        migrations.AddField(
            model_name='account',
            name='facebook_public',
            field=models.BooleanField(default=True, verbose_name='publish facebook?'),
        ),
        migrations.AddField(
            model_name='account',
            name='locality_public',
            field=models.BooleanField(default=True, verbose_name='publish locality?'),
        ),
        migrations.AddField(
            model_name='account',
            name='name_public',
            field=models.BooleanField(default=True, verbose_name='publish name?'),
        ),
    ]
