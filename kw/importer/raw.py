
class RawAccount:
	__slots__ = ["id", "name", "address", "bank_account", "bank"]
	# id str?
	# name str
	# address str
	# bank_account str
	# bank str
	def __str__(self):
		return self.id if self.id else "<" + self.nazwa + ">"

	def __repr__(self):
		return str(self)

	def __eq__(self, other):
		return self.__dict__ == other.__dict__

	def __init__(self, name="", address="", bank_account="", bank=""):
		self.id = None
		self.name = name
		self.address = address
		self.bank_account = bank_account.replace("-", "")
		self.bank = bank

class RawBankTransfer:
	__slots__ = ["id", "date", "amount", "c", "a", "title"]

	# id int
	# date date
	# amount int (grosze)
	# c RawAccount
	# a RawAccount
	# title str

	def __init__(self):
		self.c = RawAccount()
		self.a = RawAccount()

	@property
	def bank(self):
		return "BPH"

	def __str__(self):
		return str(self.id) + " " + str(self.amount/100) + " " + str(self.c) + " " + str(self.a) + " " + self.title

	def __repr__(self):
		return str(self)

	def __eq__(self, other):
		return self.__dict__ == other.__dict__
