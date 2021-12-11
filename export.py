import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "local.settings")
import django
django.setup()

from kw.models import *
import csv
import sys

def format_amount(amount):
	str_amount = str(amount)
	if len(str_amount) < 3:
		return "0." + str_amount.zfill(2)
	else:
		return str_amount[:-2] + "." + str_amount[-2:]

def print_events(w):
	w.writerow(["Data", "Wn", "Ma", "Kwota", "ID dokumentu", "Nazwa dokumentu"])
	for e in Event.objects.all():
		w.writerow([str(e.doc.date), e.dst.num_id, e.src.num_id, format_amount(e.amount), e.doc.id, e.doc])

def print_invoices(w):
	w.writerow(["ID dokumentu", "Tytuł dokumentu", "Data", "Data księgowania", "Typ", "ID wystawcy", "Nazwa wystawcy", "Numer nadany przez wystawcę", "Data sprzedaży", "ID sprzedawcy", "Nazwa sprzedawcy", "ID kupującego", "Nazwa kupującego", "Kwota", "Kwota PIT"])
	for d in Invoice.objects.all():
		w.writerow([d.id, d, str(d.date), str(d.date_posted), str(d.type.name), str(d.issuer.num_id), str(d.issuer.name), str(d.number), str(d.date_of_sale), str(d.seller.num_id), str(d.seller.name), str(d.buyer.num_id), str(d.buyer.name), format_amount(d.amount), format_amount(d.pit_amount)])

def print_banktransfers(w):
	w.writerow(["ID dokumentu", "Tytuł dokumentu", "Data", "Data księgowania", "Typ", "ID konta", "Nazwa konta", "Numer na koncie", "ID kontrahenta", "Nazwa kontrahenta", "Kwota", "Tytuł"])
	for d in BankTransfer.objects.all():
		w.writerow([d.id, d, str(d.date), str(d.date_posted), str(d.type.name), str(d.issuer.num_id), str(d.issuer.name), str(d.number), str(d.contractor.num_id), str(d.contractor.name), format_amount(d.amount), str(d.title)])

with open("events.csv", "w") as f:
	print_events(csv.writer(f))

with open("invoices.csv", "w") as f:
	print_invoices(csv.writer(f))

with open("banktransfers.csv", "w") as f:
	print_banktransfers(csv.writer(f))
