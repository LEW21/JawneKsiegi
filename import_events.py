from itertools import groupby
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jawneksiegi.settings")
import django
django.setup()

from collections import namedtuple
from pathlib import Path
from dataclasses import asdict, dataclass
from decimal import Decimal
from django.db import transaction
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
	doc_issue_date: str
	doc_title: str
	doc_party_name: str = None
	doc_party_email: str = None
	doc_party_iban: str = None

def load_journal(p):
	journal = []

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
		'payu': 3,
		'paribas': 4,
		'wydatki': 5,
		'pk': 6,
	}

	return sorted(journal, key=lambda entry: (entry.date, entry.us, module_order[entry.module], -entry.amount_pln))

def load_accounts(p):
	accounts = []

	for fname in p.glob('konta.csv'):
		with open(fname, 'r') as f:
			reader = csv.reader(f, delimiter=';')
			header = next(reader)
			RawAccount = namedtuple('RawAccount', header)
			for rawAccount in reader:
				rawAccount = RawAccount(*rawAccount)
				accounts.append(rawAccount)

	return accounts

p = Path('../ksiegi')

with transaction.atomic():
	Event.objects.all().delete()
	Document.objects.all().delete()
	Account.objects.all().delete()

	for account in load_accounts(p):
		acc = Account(num_id = account.id, name = account.name)
		acc.save()

	accounts = {acc.num_id: acc for acc in Account.objects.all()}

	def account(id):
		if '/' in id:
			account(id.rsplit('/', 1)[0])

		num_id = id.replace('-', '').replace('/', '-')

		try:
			return accounts[num_id]
		except KeyError:
			main_account = account(id.split('/')[0])
			acc, created = Account.objects.get_or_create(num_id = num_id, defaults = dict(
				name = f"{main_account.name}: {id.rsplit('/')[-1]}",
			))
			return acc

	journal = load_journal(p)

	docs = groupby(sorted(journal, key=lambda e: e.doc_id), key=lambda e: (e.us, e.doc_id))

	for (us, doc_id), entries in docs:
		entries = list(entries)

		d, created = Document.objects.get_or_create(
			issuer_name = entries[0].doc_issuer,
			number = doc_id.replace('-', '/'),
			defaults = dict(
				type = DocumentType.get('d'),
				date = entries[0].doc_issue_date or None,
			),
		)

	for entry in journal:
		src_id = entry.them if entry.amount_pln >= 0 else entry.us
		dst_id = entry.us if entry.amount_pln >= 0 else entry.them

		doc = Document.objects.get(issuer_name = entry.doc_issuer, number = entry.doc_id.replace('-', '/'))

		e = Event(
			id = f"{entry.module}#{entry.id}",
			date = entry.date,
			doc = doc,
			src = account(src_id),
			dst = account(dst_id),
			amount = int((entry.amount_pln if entry.amount_pln >= 0 else -entry.amount_pln) * 100),
			title = entry.title,
		)
		e.save()
