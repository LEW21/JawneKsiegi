# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kw', '0003_auto_20150828_1736'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='document',
            options={'verbose_name': 'document', 'verbose_name_plural': 'documents', 'ordering': ('issuer', 'number')},
        ),
        migrations.AlterUniqueTogether(
            name='document',
            unique_together=set([('issuer', 'number')]),
        ),
    ]
