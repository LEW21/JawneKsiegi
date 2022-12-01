from datetime import date
from django.db import models
from django.utils.translation import gettext_lazy as _

class Account(models.Model):
	class Meta:
		verbose_name = _('account')
		verbose_name_plural = _('accounts')
		ordering = ['num_id']

	num_id = models.CharField(_("numeric id"), max_length=30)
	name = models.CharField(_("name"), max_length=200)

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
		return self.name

	@property
	def is_nominal(self):
		return self.num_id[0] in {'4', '5', '7'}

	@property
	def is_capital(self):
		return self.num_id == '860'

	def __str__(self):
		return self.num_id + ". " + self.pub_name

	@property
	def events(self):
		ev = Event.objects.filter(models.Q(src=self) | models.Q(dst=self)).select_related("src", "dst", "doc", "doc__type")

		for e in ev:
			if e.src == self:
				e.account = e.src
				e.contractor = e.dst
				e.amount = -e.amount
			else:
				e.account = e.dst
				e.contractor = e.src

		return ev

	@property
	def past_events(self):
		return [e for e in self.events if e.date <= date.today()]

	@property
	def future_events(self):
		return [e for e in self.events if e.date > date.today()]

class Turnover(models.Model):
	class Meta:
		verbose_name = _('turnover')
		verbose_name_plural = _('turnovers')
		managed = False

	id = models.OneToOneField(Account, verbose_name=_("account"), primary_key=True, related_name="turnover", db_column="id", on_delete=models.DO_NOTHING)
	debit = models.IntegerField(_("debit"))
	credit = models.IntegerField(_("credit"))
	debit_balance = models.IntegerField(_("debit balance"))
	credit_balance = models.IntegerField(_("credit balance"))

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
		unique_together = (("issuer_name", "number"),)
		ordering = ('issuer_name', 'number')

	date = models.DateField(_("date"), null = True)
	date_posted = models.DateField(_("date posted"), auto_now_add=True)
	type = models.ForeignKey(DocumentType, on_delete=models.PROTECT, verbose_name=_("type"))
	issuer_name = models.CharField(_('issuer name'), max_length=100)
	number = models.CharField(_("number"), max_length=50)

	@property
	def url(self):
		from django.urls import reverse
		try:
			return reverse('doc', args=[self.issuer_name, self.number.replace("/", "-")])
		except:
			return ""

	def get_absolute_url(self):
		return self.url

	@property
	def number_dashed(self):
		return self.number.replace("/", "-")

	def __str__(self):
		return self.type.name.capitalize() + " " + self.issuer_name + " " + self.number

account_order = {a: i for i, a in enumerate(['86', '70', '84', '13', '20', '21', '30', '01', '02', '31', '33', '60', '64', '50', '55'])}

class Event(models.Model):
	class Meta:
		verbose_name = _('event')
		verbose_name_plural = _('events')
		ordering = ('date','-amount','title')

	id = models.CharField(max_length=100, primary_key=True)
	date = models.DateField(_("date"))
	doc = models.ForeignKey(Document, verbose_name=_("document"), related_name="events", on_delete=models.DO_NOTHING)
	amount = models.IntegerField(_("amount")) # * 0.01 PLN
	src = models.ForeignKey(Account, verbose_name=_("from"), related_name="events_from", on_delete=models.DO_NOTHING)
	dst = models.ForeignKey(Account, verbose_name=_("to"), related_name="events_to", on_delete=models.DO_NOTHING)
	title = models.TextField(null=True)

	@property
	def _shall_reverse(self):
		return min([(account_order[self.src.num_id[:2]], 0), (account_order[self.dst.num_id[:2]], 1)])[1]

	@property
	def left(self):
		return [self.src, self.dst][self._shall_reverse]

	@property
	def right(self):
		return [self.dst, self.src][self._shall_reverse]

	@property
	def ltr_amount(self):
		return [self.amount, -self.amount][self._shall_reverse]

	def __str__(self):
		return str(self.doc.date) + ": " + str(self.src) + " -> " + str(self.dst) + ": " + str(self.amount)
