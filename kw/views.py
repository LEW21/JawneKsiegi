from __future__ import annotations

from dataclasses import dataclass
from datetime import date as Date
from django.shortcuts import render, redirect
from django.http import Http404
from .models import *
from .sheet import BalanceSheetAccount, make_side, debit_template, credit_template

def index(request):
	return redirect("date_accounts", date.today().isoformat(), permanent=False)

def flatten_sheet(accounts: list[BalanceSheetAccount]):
	for acc in accounts:
		yield acc
		yield from flatten_sheet(acc.subaccounts)

def date_accounts(request, date: str):
	world.date = Date.fromisoformat(date)

	book = Book()

	return render(request, 'kw/index.html', {
		'world_date': world.date,
		'top_accounts': book,
		'debit_sheet_accounts': flatten_sheet(make_side('debit', 0, debit_template, book)),
		'credit_sheet_accounts': flatten_sheet(make_side('credit', 0, credit_template, book)),
	})

def date_account(request, date: str, acc_id: str):
	world.date = Date.fromisoformat(date)

	try:
		a = Account.objects.get(num_id=acc_id)
	except Account.DoesNotExist:
		raise Http404

	pev = a.past_events

	balance = 0
	for e in pev:
		balance += e.amount
		e.balance = balance
	cbalance = balance

	fev = a.future_events
	for e in fev:
		balance += e.amount
		e.balance = balance
	fbalance = balance

	return render(request, 'kw/index.html', {
		'world_date': world.date,
		'account': a,
		'events': pev,
		'future_events': fev,
		'balance': cbalance,
		'future_balance': fbalance,
	})

@dataclass
class Actor:
	name: str
	issued_documents: list[Document]

	def __str__(self):
		return self.name

def date_party(request, date: str, party_id: str):
	world.date = Date.fromisoformat(date)

	docs = list(Document.objects.filter(issuer_name = party_id).order_by('date'))
	if len(docs) == 0:
		raise Http404

	return render(request, 'kw/actor.html', {
		'world_date': world.date,
		'actor': Actor(
			name = party_id,
			issued_documents = docs
		)
	})

def date_doc(request, date: str, party_id: str, doc_id: str):
	world.date = Date.fromisoformat(date)

	try:
		d = Document.objects.get(issuer_name = party_id, number = doc_id.replace("-", "/"))
	except Document.DoesNotExist:
		raise Http404

	return render(request, 'kw/doc.html', {
		'world_date': world.date,
		'doc': d
	})
