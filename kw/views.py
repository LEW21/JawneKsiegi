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

	tr = obj_list([x.banktransfer for x in a.documents.filter(type_id="P").select_related("banktransfer", "banktransfer__contractor", "banktransfer__issuer", "banktransfer__type")])

	balance = 0
	for t in tr:
		balance += t.amount
		t.balance = balance
	tr.balance = balance

	ev = a.events

	balance = 0
	for e in ev:
		balance += e.amount
		e.balance = balance
	ev.balance = balance

	return render(request, 'kw/index.html', {
		'account': a,
		'transfers': tr,
		'events': ev,
	})

def doc(request, acc_id, doc_id):
	try:
		a = Account.objects.get(num_id=acc_id)
	except Account.DoesNotExist:
		try:
			a = Account.objects.get(shortcut=acc_id)
		except Account.DoesNotExist:
			raise Http404
		return redirect("account", a.num_id, permanent=True)

	try:
		d = a.documents.select_related("banktransfer__issuer", "invoice__issuer", "banktransfer__type", "invoice__type", "banktransfer__contractor", "invoice__seller", "invoice__buyer").prefetch_related(Prefetch("banktransfer__events", queryset = Event.objects.select_related("src", "dst"))).prefetch_related("banktransfer__files").prefetch_related(Prefetch("invoice__events", queryset = Event.objects.select_related("src", "dst"))).prefetch_related("invoice__files").get(number=doc_id.replace("-", "/"))
	except Document.DoesNotExist:
		raise Http404

	try:
		d = d.banktransfer
	except:
		d = d.invoice

	return render(request, 'kw/doc.html', {
		'doc': d
	})
