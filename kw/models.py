from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class Account(models.Model):
	class Meta:
		verbose_name = _('account')
		verbose_name_plural = _('accounts')
		ordering = ['num_id']

	num_id = models.CharField(_("numeric id"), max_length=30)
	shortcut = models.CharField(_("shortcut"), max_length=30, blank=True)
	name = models.CharField(_("name"), max_length=200)
	address = models.CharField(_("address"), max_length=200, blank=True)
	bank_account = models.CharField(_("bank account"), max_length=200, blank=True)
	locality = models.CharField(_("locality"), max_length=200, blank=True)
	facebook_id = models.CharField(_("facebook id"), max_length=50, blank=True)

	name_public = models.BooleanField(_("publish name?"), default=True)
	locality_public = models.BooleanField(_("publish locality?"), default=True)
	address_public = models.BooleanField(_("publish address?"), default=False)
	bank_account_public = models.BooleanField(_("publish bank account?"), default=False)
	facebook_public = models.BooleanField(_("publish facebook?"), default=True)

	@property
	def url(self):
		from django.urls import reverse
		return reverse('account', args=[str(self.num_id)])

	def get_absolute_url(self):
		return self.url

	@property
	def level(self):
		return self.num_id.count("-")

	@property
	def levelP1(self):
		return self.level + 1

	@property
	def local_id(self):
		return self.num_id.rsplit("-", 1)[-1]

	@property
	def parent_id(self):
		try:
			return self.num_id.rsplit("-", 1)[-2]
		except:
			return None

	@property
	def parent(self):
		try:
			return self.parent_cache
		except:
			self.parent_cache = Account.objects.get(num_id=self.parent_id)
			return self.parent_cache

	@property
	def children(self):
		return Account.objects.filter(num_id__startswith=self.num_id + "-").select_related("turnover")

	@property
	def pub_name(self):
		if self.name_public:
			return self.name

		return "".join(x[0] if len(x) else "" for x in self.name.split(" "))

	@property
	def is_nominal(self):
		return self.num_id >= "400"

	@property
	def shortname(self):
		if self.shortcut:
			return self.shortcut

		if len(self.pub_name) < 20:
			return self.pub_name
		return self.pub_name[0:19] + "…"

	def __str__(self):
		return self.num_id + ". " + self.pub_name

	@property
	def events(self):
		ev = Event.objects.filter(models.Q(src=self) | models.Q(dst=self)).select_related("src", "dst", "doc", "doc__issuer", "doc__type")

		for e in ev:
			if e.src == self:
				e.account = e.src
				e.contractor = e.dst
				e.amount = -e.amount
			else:
				e.account = e.dst
				e.contractor = e.src

		ev = sorted(ev, key=lambda e: (e.doc.date, -e.amount))
		return ev

class AccountRelationType(models.Model):
	class Meta:
		verbose_name = _('account relation type')
		verbose_name_plural = _('account relation types')

	text_id = models.CharField(_("text id"), max_length=30)

	def __str__(self):
		return self.text_id

class AccountRelation(models.Model):
	class Meta:
		verbose_name = _('account relation')
		verbose_name_plural = _('account relations')

	src = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name=_("from"), related_name="relations_from")
	type = models.ForeignKey(AccountRelationType, on_delete=models.PROTECT, verbose_name=_("type"))
	dst = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name=_("to"), related_name="relations_to")

	def __str__(self):
		return str(self.src) + " =" + str(self.type) + "> " + str(self.dst)

class Turnover(models.Model):
	class Meta:
		verbose_name = _('turnover')
		verbose_name_plural = _('turnovers')
		managed = False

	id = models.OneToOneField(Account, verbose_name=_("account"), primary_key=True, related_name="turnover", db_column="id", on_delete=models.DO_NOTHING)
	debit = models.IntegerField(_("debit"))
	credit = models.IntegerField(_("credit"))
	balance = models.IntegerField(_("balance"))

def format_amount(amount, add_sign = True):
	sign = 1 if amount > 0 else -1 if amount < 0 else 0
	abs_amount = amount if sign >= 0 else -amount
	return ("+" if sign > 0 and add_sign else "-" if sign < 0 else "") + str(int(abs_amount/100)) + "." + str(abs_amount%100).zfill(2)

class DocumentType(models.Model):
	class Meta:
		verbose_name = _('document type')
		verbose_name_plural = _('document types')

	id = models.CharField(_("id"), primary_key=True, max_length=1)
	name = models.CharField(_("name"), max_length=30)

	def __str__(self):
		return self.name

	cache = {}
	@classmethod
	def get(cls, id):
		try:
			return cls.cache[id]
		except:
			cls.cache[id] = cls.objects.get(id=id)
			return cls.cache[id]

class Document(models.Model):
	class Meta:
		verbose_name = _('document')
		verbose_name_plural = _('documents')
		unique_together = (("issuer", "number"),)
		ordering = ('issuer', 'number')

	date = models.DateField(_("tax point date"))
	date_posted = models.DateField(_("date posted"), auto_now_add=True)
	#date_posted.editable = True
	type = models.ForeignKey(DocumentType, on_delete=models.PROTECT, verbose_name=_("type"))
	issuer = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name=_("issuer"), related_name="documents")
	number = models.CharField(_("number"), max_length=50)

	@property
	def url(self):
		from django.urls import reverse
		return reverse('doc', args=[self.issuer.num_id, self.number.replace("/", "-")])

	def get_absolute_url(self):
		return self.url

	@property
	def number_dashed(self):
		return self.number.replace("/", "-")

	def __str__(self):
		return self.type.name.capitalize() + " " + self.issuer.shortname + " " + self.number

class BankTransfer(Document):
	class Meta:
		verbose_name = _('bank transfer')
		verbose_name_plural = _('bank transfers')

	contractor = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name=_("contractor"), related_name="foreign_transfers", limit_choices_to=~models.Q(num_id__startswith=4))
	amount = models.IntegerField(_("amount")) # * 0.01 PLN
	title = models.CharField(_("title"), max_length=200)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.type = DocumentType.get("P")

class Invoice(Document):
	class Meta:
		verbose_name = _('invoice')
		verbose_name_plural = _('invoices')

	date_of_sale = models.DateField(_("date of sale"))
	seller = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name= _("seller"), related_name="sold")
	buyer = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name=_("buyer"), related_name="bought", default=1)
	pit_amount = models.IntegerField(_("PIT amount"), default=0)

	@property
	def amount(self):
		return sum(l.amount for l in self.lines.all())

class InvoiceLine(models.Model):
	class Meta:
		verbose_name = _('invoice line')
		verbose_name_plural = _('invoice lines')

	invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, verbose_name=_("invoice"), related_name="lines")
	number = models.IntegerField(_("number"))
	account = models.ForeignKey(Account, on_delete=models.PROTECT, verbose_name=_("account"))
	amount = models.IntegerField(_("amount"))

	def __str__(self):
		return str(self.invoice) + ": " + str(self.number) + ". " + str(self.account) + " " + str(self.amount)

class Event(models.Model):
	class Meta:
		verbose_name = _('event')
		verbose_name_plural = _('events')

	id = models.CharField(max_length=100, primary_key=True)
	doc = models.ForeignKey(Document, verbose_name=_("document"), related_name="events", on_delete=models.DO_NOTHING)
	amount = models.IntegerField(_("amount")) # * 0.01 PLN
	src = models.ForeignKey(Account, verbose_name=_("from"), related_name="events_from", on_delete=models.DO_NOTHING)
	dst = models.ForeignKey(Account, verbose_name=_("to"), related_name="events_to", on_delete=models.DO_NOTHING)

	def __str__(self):
		return str(self.doc.date) + ": " + str(self.src) + " -> " + str(self.dst) + ": " + str(self.amount)

def upload_to(a, user_filename):
	return "attachments/" + str(uuid.uuid4()).replace("-", "") + "." + user_filename.rsplit(".", 1)[1]

class Attachment(models.Model):
	class Meta:
		verbose_name = _('attachment')
		verbose_name_plural = _('attachments')

	doc = models.ForeignKey(Document, on_delete=models.CASCADE, verbose_name=_("document"), related_name="files")
	name = models.CharField(_("name"), max_length=100)
	file = models.FileField(_("file"), upload_to=upload_to)
	public = models.BooleanField(_("public"), default=True)

	@property
	def url(self):
		return self.file.url

	def get_absolute_url(self):
		return self.url

	def __str__(self):
		return str(self.doc) + " - " + self.name
