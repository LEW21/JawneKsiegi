#!/usr/bin/env python3

from . import bph
from .accounts import identify
from ..models import BankTransfer
from django.db.utils import IntegrityError
from django.utils.translation import ugettext as _

def import_file(filename):
	data = list(bph.data(filename))

	for op in data:
		bt = BankTransfer()
		bt.date = op.date
		bt.issuer = identify(op.a)
		bt.number = str(op.id)
		bt.contractor = identify(op.c)
		bt.amount = op.amount
		bt.title = op.title

		try:
			bt.save()
			print(_("Imported: ") + str(bt))
		except IntegrityError:
			print(_("Skipping: ") + str(bt))
