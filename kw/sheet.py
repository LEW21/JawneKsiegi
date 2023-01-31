from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Union
from enum import Enum

from .models import Book, Account

class SpecialAccount(Enum):
	current_result = object()
	past_results = object()

debit_template = {
	"Aktywa": {
		"A. Aktywa trwałe": {
			"I. Wartości niematerialne i prawne": {"020"},
			"II. Rzeczowe aktywa trwałe": {"010"},
			"III. Należności długoterminowe": {},
			"IV. Inwestycje długoterminowe": {},
			"V. Długoterminowe rozliczenia międzyokresowe": {},
		},
		"B. Aktywa obrotowe": {
			"I. Zapasy": {"310"},
			"II. Należności krótkoterminowe": {"200", "301", "302", "303"},
			"III. Inwestycje krótkoterminowe": {"130"},
			"IV. Krótkoterminowe rozliczenia międzyokresowe": {"640"},
		},
		"C. Należne wpłaty na fundusz statutowy": {},
	},
}

credit_template = {
	"Pasywa": {
		"A. Fundusz własny": {
			"I. Fundusz statutowy": {},
			"II. Pozostałe fundusze": {},
			"III. Zysk (strata) z lat ubiegłych": {SpecialAccount.past_results},
			"IV. Zysk (strata) netto": {SpecialAccount.current_result},
		},
		"B. Zobowiązania i rezerwy na zobowiązania": {
			"I. Rezerwy na zobowiązania": {"840"},
			"II. Zobowiązania długoterminowe": {},
			"III. Zobowiązania krótkoterminowe": {"200", "301", "302", "303", "130", "310"},
			"IV. Rozliczenia międzyokresowe": {"640"},
		}
	},
}

SheetTemplate = dict[str, Union["SheetTemplate", set[str|SpecialAccount]]]

@dataclass
class BalanceSheetAccount:
	side: Literal['debit', 'credit']
	level: int
	full_name: str
	subaccounts: list[BalanceSheetAccount]
	book_accounts: list[Account]

	@property
	def local_id(self):
		return self.full_name.rpartition('. ')[0]

	@property
	def name(self):
		return self.full_name.rpartition('. ')[2]

	@property
	def amount(self):
		return sum(acc.amount for acc in self.subaccounts) + sum(acc.debit_balance if self.side == 'debit' else acc.credit_balance for acc in self.book_accounts)

def make_side(side: Literal['debit', 'credit'], level: int, template: SheetTemplate, book: Book):
	for name, subtemplate in template.items():
		if isinstance(subtemplate, dict):
			subaccounts = list[BalanceSheetAccount](make_side(side, level + 1, subtemplate, book))
			book_accounts = []
		else:
			subaccounts = []
			book_ids: list[str] = [v for v in subtemplate if isinstance(v, str)]
			book_accounts = sum(([book_account for book_account in book.balance.children if book_account.num_id.startswith(book_id)] for book_id in book_ids), start=[])
			if SpecialAccount.current_result in subtemplate:
				book_accounts.append(book.current_result)
			if SpecialAccount.past_results in subtemplate:
				book_accounts.append(book.past_results)
		yield BalanceSheetAccount(side, level, name, subaccounts, book_accounts)
