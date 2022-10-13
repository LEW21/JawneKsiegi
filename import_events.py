from itertools import groupby
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jawneksiegi.settings")
import django
django.setup()

from collections import namedtuple
from pathlib import Path
from dataclasses import asdict, dataclass
from decimal import Decimal
import csv

from kw.models import *

@dataclass
class Entry:
	module: str
	id: int
	date: str
	us: str
	them: str
	amount_pln: Decimal
	title: str

	doc_issuer: str
	doc_id: str
	doc_title: str
	doc_party_name: str = None
	doc_party_email: str = None
	doc_party_iban: str = None

def load_journal():
	journal = []
	p = Path('.')

	for fname in p.glob('dziennik.csv'):
		with open(fname, 'r') as f:
			reader = csv.reader(f, delimiter=';')
			header = next(reader)
			RawEntry = namedtuple('RawEntry', header)
			for rawEntry in reader:
				rawEntry = RawEntry(*rawEntry)
				entry = Entry(**rawEntry._asdict())
				entry.amount_pln = Decimal(entry.amount_pln)
				journal.append(entry)

	module_order = {
		'patronite': 1,
		'zrzutka': 2,
		'paribas': 3,
		'wydatki': 4,
		'zamkniecie': 5,
	}

	return sorted(journal, key=lambda entry: (entry.date, entry.us, module_order[entry.module], -entry.amount_pln))


journal = load_journal()

accounts = {acc.num_id: acc for acc in Account.objects.all()}

def account(name):
	num_id = name.replace('-', '').replace('/', '-')

	try:
		return accounts[num_id]
	except KeyError:
		acc, created = Account.objects.get_or_create(num_id = num_id, defaults=dict(
			name = name,
		))
		return acc

Event.objects.all().delete()
Document.objects.all().delete()

docs = groupby(sorted(journal, key=lambda e: e.doc_id), key=lambda e: (e.us, e.doc_id))

for (us, doc_id), entries in docs:
	entries = list(entries)

	if us.startswith('1'):
		d, created = BankTransfer.objects.get_or_create(
			issuer = account(us),
			number = doc_id.replace('-', '/'),
			defaults = dict(
				date = entries[0].date,
				contractor = Account.objects.get(num_id = '999'),
				title = entries[0].doc_title,
				amount = sum(e.amount_pln for e in entries) * 100,
			),
		)
	else:
		d, created = Document.objects.get_or_create(
			issuer = account(us),
			number = doc_id.replace('-', '/'),
			type = DocumentType.get('d'),
			defaults = dict(
				date = entries[0].date,
			),
		)

for entry in journal:
	src_id = entry.them if entry.amount_pln >= 0 else entry.us
	dst_id = entry.us if entry.amount_pln >= 0 else entry.them

	doc = Document.objects.get(issuer = account(entry.us), number = entry.doc_id.replace('-', '/'))

	e = Event(
		id = f"{entry.module}#{entry.id}",
		doc = doc,
		src = account(src_id),
		dst = account(dst_id),
		amount = int((entry.amount_pln if entry.amount_pln >= 0 else -entry.amount_pln) * 100),
	)
	e.save()
