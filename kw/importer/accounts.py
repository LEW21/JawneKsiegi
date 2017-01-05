from ..models import Account
from random import randint

def clear_name(name):
	base = name.lower().strip().replace(".", "").replace(" ", "")

	if "(" in base:
		base = base.split("(")[0].strip()

	if base.endswith("sa"):
		base = base[:-2]
	elif base.endswith("sc"):
		base = base[:-2]
	elif base.endswith("spzoo"):
		base = base[:-5]
	if base.endswith("pl"):
		base = base[:-2]
	return base

def text_id(name):
	if name.count('"') == 2:
		return name.split('"')[1]

	base = name.upper().strip().replace(".", "").replace('"', "").replace("-", " ")

	if base.endswith(" SA"):
		base = base[:-3]
	elif base.endswith(" SC"):
		base = base[:-3]
	elif base.endswith(" SPZOO"):
		base = base[:-6]
	elif base.endswith(" SP ZOO"):
		base = base[:-7]
	elif base.endswith(" SP Z OO"):
		base = base[:-8]
	if base.endswith("PL"):
		base = base[:-2]

	base = base.strip()

	if len(base) < 5 or not " " in base:
		return base

	return "".join(x[0] for x in base.split(" "))

def na(acc):
	return clear_name(acc.name) + acc.bank_account

by_na = {}

for a in Account.objects.all():
	by_na[na(a)] = a

def get_next_id():
	try:
		a = Account.objects.filter(num_id__startswith="200-").order_by("-num_id")[0]
	except:
		return 1

	return int(a.num_id[4:]) + 1

next_id = get_next_id()

def identify(acc):
	global next_id
	try:
		return by_na[na(acc)]
	except:
		a = Account()
		a.num_id = "200-" + str(next_id).zfill(4)
		next_id += 1
		a.text_id = text_id(acc.name)
		a.name = acc.name
		a.locality = acc.address.rsplit(" ", 1)[1]
		a.address = acc.address
		a.bank_account = acc.bank_account
		a.save()
		by_na[na(a)] = a
		return a
