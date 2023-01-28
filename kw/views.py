from dataclasses import dataclass
from django.shortcuts import render, redirect
from django.http import Http404
from .models import *

def index(request):
	return redirect("accounts", permanent=False)

def accounts(request):
	accounts = TopAccounts()

	return render(request, 'kw/index.html', {
		'top_accounts': accounts,
	})

def account(request, acc_id):
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

def actor(request, actor_id):
	docs = list(Document.objects.filter(issuer_name = actor_id).order_by('date'))
	if len(docs) == 0:
		raise Http404

	return render(request, 'kw/actor.html', {
		'actor': Actor(
			name = actor_id,
			issued_documents = docs
		)
	})

def doc(request, actor_id, doc_id):
	try:
		d = Document.objects.get(issuer_name = actor_id, number = doc_id.replace("-", "/"))
	except Document.DoesNotExist:
		raise Http404

	return render(request, 'kw/doc.html', {
		'doc': d
	})
