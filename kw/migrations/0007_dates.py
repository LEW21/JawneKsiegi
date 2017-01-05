# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

	dependencies = [
		('kw', '0006_shortcut'),
	]

	operations = [
		migrations.AddField(
			model_name='document',
			name='date_posted',
			field=models.DateField(default=datetime.date(2015, 1, 1), auto_now_add=True, verbose_name='date posted'),
			preserve_default=False,
		),
		migrations.AddField(
			model_name='invoice',
			name='date_of_sale',
			field=models.DateField(default=datetime.date(2015, 1, 1), verbose_name='date of sale'),
			preserve_default=False,
		),
	]
