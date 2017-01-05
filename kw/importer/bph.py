import csv
import os

from datetime import date
from decimal import Decimal
from .raw import RawAccount, RawBankTransfer

desc = """
id Numer sekwencyjny

ref_banku Referencje banku

data_efektywna Data efektywna
data_ksiegowania Data księgowania
data_obciazenia_k Data obciążenia rachunku nadawcy

k_nazwa Nazwa kontrahenta
k_adres Adres kontrahenta
k_rachunek Rachunek kontrahenta
k_bank Bank kontrahenta

w_nazwa Nazwa właściciela
w_adres Adres właściciela
w_rachunek Rachunek właściciela
w_bank Bank prowadzący rachunek

kod_op Kod operacji
kod_op_opis Opis kodu operacji
typ_op Typ operacji

tytul Tytuł operacji
kwota Kwota
waluta Waluta
saldo Saldo po operacji
"""

def parse_desc(desc):
	for field in desc.splitlines():
		if not field:
			continue

		yield tuple(field.split(" ", 1))

def s_to_numbers(fields, header):
	for d_name, s_name in fields:
		yield d_name, header.index(s_name)

def nowaStrona(t, f):
	return RawAccount(f(t + "_nazwa"), f(t + "_adres"), f(t + "_rachunek"), f(t + "_bank"))

def nowaOperacja(f):
	r = RawBankTransfer()

	r.id = int(f("id"))

	d = f("data_ksiegowania")
	r.date = date(int(d[0:4]), int(d[5:7]), int(d[8:10]))

	r.amount = int(Decimal(f("kwota").replace(",", ".")) * 100)

	r.c = nowaStrona("k", f)
	r.a = nowaStrona("w", f)

	if len(r.c.name) == 0 and f("kod_op") > "800":
		r.c = RawAccount("Bank BPH", "", "", "BPH")

	r.title = f("tytul")

	return r

def data(filename):
	data = csv.reader(open(filename, "r"), delimiter=";")

	header = next(data)

	F = {name: pos for name, pos in s_to_numbers(parse_desc(desc), header)}

	for row in data:
		def f(x):
			return row[F[x]]

		yield nowaOperacja(f)
