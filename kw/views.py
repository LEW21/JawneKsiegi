from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from django.db.models import Prefetch
from django.http import Http404

def index(request):
	return redirect("accounts", permanent=False)

def accounts(request):
	return render(request, 'kw/index.html', {
		'accounts': Account.objects.select_related("turnover").all()
	})

class obj_list(list):
	pass

def account(request, acc_id):
	try:
		a = Account.objects.get(num_id=acc_id)
	except Account.DoesNotExist:
		try:
			a = Account.objects.get(shortcut=acc_id)
		except Account.DoesNotExist:
			raise Http404
		return redirect("account", a.num_id, permanent=True)

	"""
	tr = obj_list([x.banktransfer for x in a.documents.filter(type_id="P").select_related("banktransfer", "banktransfer__contractor", "banktransfer__issuer", "banktransfer__type")])

	balance = 0
	for t in tr:
		balance += t.amount
		t.balance = balance
	tr.balance = balance
	"""
	tr = []

	ev = a.events

	balance = 0
	for e in ev:
		balance += e.amount
		e.balance = balance

	return render(request, 'kw/index.html', {
		'account': a,
		'transfers': tr,
		'events': ev,
		'balance': balance,
	})

def doc(request, acc_id, doc_id):
	try:
		d = Document.objects.get(issuer_name = acc_id, number = doc_id.replace("-", "/"))
	except Document.DoesNotExist:
		raise Http404

	try:
		d = d.banktransfer
	except:
		try:
			d = d.invoice
		except:
			pass

	return render(request, 'kw/doc.html', {
		'doc': d
	})
