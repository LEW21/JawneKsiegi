from __future__ import annotations

from abc import abstractmethod
from datetime import date
from dataclasses import dataclass
from typing import TypeVar
from django.db import models
from django.utils.translation import gettext_lazy as _

class AccountMixin:
	@property
	@abstractmethod
	def num_id(self) -> str:
		...

	@property
	@abstractmethod
	def level(self) -> int:
		...

	@property
	@abstractmethod
	def _children(self) -> models.BaseManager[Account]:
		...

	@property
	@abstractmethod
	def is_nominal(self) -> bool:
		...

	@property
	def levelP1(self):
		return self.level + 1

	@property
	def children(self) -> list[Account]:
		accounts = list(self._children.select_related('own_turnover'))
		acc_by_id = {self.num_id: self}
		self.debit_turnover = 0
		self.credit_turnover = 0
		self.debit_balance = 0
		self.credit_balance = 0
		for acc in accounts:
			acc.debit_turnover = acc.own_turnover.debit
			acc.credit_turnover = acc.own_turnover.credit
			acc.debit_balance = acc.own_turnover.debit_balance
			acc.credit_balance = acc.own_turnover.credit_balance
			acc_by_id[acc.num_id] = acc
			ancestor = acc
			while (ancestor.num_id and (ancestor := acc_by_id.get(ancestor.parent_id, None))):
				ancestor.debit_turnover += acc.debit_turnover
				ancestor.credit_turnover += acc.credit_turnover
				ancestor.debit_balance += acc.debit_balance
				ancestor.credit_balance += acc.credit_balance

		return accounts

@dataclass
class TopAccount(AccountMixin):
	num_id = None
	level = -1
	is_nominal: bool = None
	_children: models.BaseManager[Account] = None

class TopAccounts:
	def __init__(self):
		self.balance = TopAccount(False, Account.objects.exclude(num_id__startswith='7'))
		self.nominal = TopAccount(True, Account.objects.filter(num_id__startswith='7'))

class Account(AccountMixin, models.Model):
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
	def local_id(self):
		return self.num_id.rsplit("-", 1)[-1]

	@property
	def top_id(self):
		return self.num_id.partition('-')[0]

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
	def _children(self):
		return Account.objects.filter(num_id__startswith=self.num_id + "-")

	@property
	def pub_name(self):
		return self.name

	@property
	def is_nominal(self):
		return self.num_id[0] == '7'

	def __str__(self):
		return self.num_id + ". " + self.pub_name

	@dataclass
	class AccountEvent:
		entry: Event
		date: date
		account: Account
		contractor: Account
		amount: int
		count: int
		doc: Document
		item_id: str
		item_name: str
		title: str

	@property
	def events(self) -> list[AccountEvent]:
		eventss = []
		for e in Event.objects.filter(models.Q(src=self) | models.Q(dst=self)).select_related("src", "dst", "doc", "doc__type"):
			events = []
			if e.src == self:
				events.append(self.AccountEvent(e, e.date, e.src, e.dst, -e.amount, -e.count if e.count is not None else None, e.doc, e.item_id, e.item_name, e.title))
			if e.dst == self:
				events.append(self.AccountEvent(e, e.date, e.dst, e.src, e.amount, e.count if e.count is not None else None, e.doc, e.item_id, e.item_name, e.title))
			eventss.append(events)
		return sum(sorted(eventss, key=lambda es: (es[0].date, es[0].doc.id, -abs(es[0].amount), es[0].amount)), [])

	@property
	def past_events(self):
		return [e for e in self.events if e.date <= date.today()]

	@property
	def future_events(self):
		return [e for e in self.events if e.date > date.today()]

class Turnover_Own(models.Model):
	class Meta:
		verbose_name = _('turnover')
		verbose_name_plural = _('turnovers')
		managed = False

	id = models.OneToOneField(Account, verbose_name=_("account"), primary_key=True, related_name="own_turnover", db_column="id", on_delete=models.DO_NOTHING)
	debit = models.IntegerField(_("debit"))
	credit = models.IntegerField(_("credit"))
	balance = models.IntegerField()
	@property
	def credit_balance(self):
		return max(-self.balance, 0)
	@property
	def debit_balance(self):
		return max(self.balance, 0)

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

from collections import defaultdict
from graphlib import TopologicalSorter, CycleError

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

	@property
	def nicely_sorted_events(self):
		all_events = self.events.all()
		graph = defaultdict(list)
		for ev in all_events:
			graph[ev.dst_id].append(ev.src_id)
		try:
			order = TopologicalSorter(graph).static_order()
			for src_id in order:
				yield from [ev for ev in all_events if ev.src_id == src_id]
		except CycleError:
			yield from all_events

class Event(models.Model):
	class Meta:
		verbose_name = _('event')
		verbose_name_plural = _('events')
		ordering = ('date','-amount','title')

	id = models.CharField(max_length=100, primary_key=True)
	date = models.DateField(_("date"))
	doc = models.ForeignKey(Document, verbose_name=_("document"), related_name="events", on_delete=models.DO_NOTHING)
	src = models.ForeignKey(Account, verbose_name=_("from"), related_name="events_from", on_delete=models.DO_NOTHING)
	dst = models.ForeignKey(Account, verbose_name=_("to"), related_name="events_to", on_delete=models.DO_NOTHING)
	amount = models.IntegerField(_("amount")) # * 0.01 PLN
	count = models.IntegerField(_("count"), null=True) # * 0.01
	item_id = models.CharField(max_length=50)
	item_name = models.CharField(max_length=100)

	title = models.TextField(null=True)

	def __str__(self):
		return str(self.doc.date) + ": " + str(self.src) + " -> " + str(self.dst) + ": " + str(self.amount)
