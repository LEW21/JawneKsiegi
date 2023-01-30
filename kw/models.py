from __future__ import annotations

from abc import abstractmethod
from datetime import date
from dataclasses import dataclass, field
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db import connection
from itertools import chain
import threading

world = threading.local()

@dataclass(frozen=True)
class AbstractAccount:
	@property
	@abstractmethod
	def num_id(self) -> str:
		...

	@property
	@abstractmethod
	def name(self) -> str:
		...

	@property
	def url(self):
		from django.urls import reverse
		return reverse('date_account', args=[world.date.isoformat(), str(self.num_id)])

	def get_absolute_url(self):
		return self.url

	@property
	def level(self):
		return self.num_id.count("-") if self.num_id else -1

	@property
	def levelP1(self):
		return self.level + 1

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
	def pub_name(self):
		return self.name

	@property
	def is_nominal(self):
		return self.num_id[0] == '7'

	def __str__(self):
		return self.num_id + ". " + self.pub_name

	@property
	def descendants(self) -> list[Account]:
		try:
			return self._descendants
		except AttributeError:
			pass

		SQL = lambda where: f"""
			SELECT a.num_id, a.name, coalesce(debit, 0) as own_debit, coalesce(credit, 0) as own_credit, coalesce(debit, 0)-coalesce(credit, 0) as own_balance
			FROM kw_account a
			LEFT JOIN (
					SELECT k.id as acc, sum(dst.amount) as debit FROM kw_account k
					LEFT JOIN kw_event dst ON k.id = dst.dst_id AND dst.date <= %s
					GROUP BY k.id) wn ON wn.acc = a.id
			LEFT JOIN (
					SELECT k.id as acc, sum(src.amount) as credit FROM kw_account k
					LEFT JOIN kw_event src ON k.id = src.src_id AND src.date <= %s
					GROUP BY k.id) ma ON ma.acc = a.id
			WHERE {where}
			ORDER BY a.num_id ASC;
		"""

		with connection.cursor() as cursor:
			if self.num_id:
				cursor.execute(SQL("""(a."num_id" LIKE %s)"""), [world.date, world.date, self.num_id + '-%'])
			elif self.is_nominal:
				cursor.execute(SQL("""(a."num_id" LIKE '7%%')"""), [world.date, world.date])
			else:
				cursor.execute(SQL("""(a."num_id" NOT LIKE '7%%')"""), [world.date, world.date])

			acc_by_id = {}
			for acc in chain([self], (NormalAccount(*row) for row in cursor)):
				object.__setattr__(acc, '_descendants', [])
				acc_by_id[acc.num_id] = acc
				ancestor = acc
				while (ancestor.num_id and (ancestor := acc_by_id.get(ancestor.parent_id, None))):
					ancestor._descendants.append(acc)

		return self._descendants

	@property
	def children(self) -> list[Account]:
		return [acc for acc in self.descendants if acc.level == self.level + 1]

	@property
	def debit_turnover(self) -> int:
		return sum(acc.own_debit for acc in [self] + self.descendants)

	@property
	def credit_turnover(self) -> int:
		return sum(acc.own_credit for acc in [self] + self.descendants)

	@property
	def debit_balance(self) -> int:
		return sum(max(acc.own_balance, 0) for acc in [self] + self.descendants)

	@property
	def credit_balance(self) -> int:
		return sum(max(-acc.own_balance, 0) for acc in [self] + self.descendants)

	@property
	def descendants_debit_turnover(self) -> int:
		return sum(acc.own_debit for acc in self.descendants)

	@property
	def descendants_credit_turnover(self) -> int:
		return sum(acc.own_credit for acc in self.descendants)

	@property
	def descendants_debit_balance(self) -> int:
		return sum(max(acc.own_balance, 0) for acc in self.descendants)

	@property
	def descendants_credit_balance(self) -> int:
		return sum(max(-acc.own_balance, 0) for acc in self.descendants)

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
		return [e for e in self.events if e.date <= world.date]

	@property
	def future_events(self):
		return [e for e in self.events if e.date > world.date]

@dataclass(frozen=True)
class NormalAccount(AbstractAccount):
	num_id: str = field(default=None)
	name: str = field(default=None)
	own_debit: int = field(default=None)
	own_credit: int = field(default=None)
	own_balance: int = field(default=None)

@dataclass(frozen=True)
class TopAccount(AbstractAccount):
	is_nominal: bool = field(default=None)

	num_id = None
	name = ""
	own_debit = 0
	own_credit = 0
	own_balance = 0

class Book:
	def __init__(self):
		self.balance = TopAccount(False)
		self.nominal = TopAccount(True)

	@property
	def current_result(self):
		return CurrentResult(self)

	@property
	def past_results(self):
		return PastResults(self)

class CurrentResult:
	def __init__(self, book: Book):
		self.book = book

	@property
	def debit_balance(self):
		return 0

	@property
	def credit_balance(self):
		return sum(sum(child.credit_balance - child.debit_balance for child in acc.children if int(child.local_id) == world.date.year) for acc in self.book.nominal.children)

class PastResults:
	def __init__(self, book: Book):
		self.book = book

	@property
	def debit_balance(self):
		return 0

	@property
	def credit_balance(self):
		return sum(sum(child.credit_balance - child.debit_balance for child in acc.children if int(child.local_id) < world.date.year) for acc in self.book.nominal.children)

class Account(models.Model, AbstractAccount):
	num_id = models.TextField()
	name = models.TextField()

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
			return reverse('date_doc', args=[world.date.isoformat(), self.issuer_name, self.number.replace("/", "-")])
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
