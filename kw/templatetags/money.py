from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

def format_amount(amount, add_sign = True):
	if amount is None:
		return ''
	sign = 1 if amount > 0 else -1 if amount < 0 else 0
	abs_amount = amount if sign >= 0 else -amount
	return ("+" if sign > 0 and add_sign else "-" if sign < 0 else "") + str(int(abs_amount/100)) + "." + str(abs_amount%100).zfill(2)

@register.filter
def money(value):
	return format_amount(value, False)

@register.filter
def money_sign(value):
	return format_amount(value, True)

@register.filter
def debit(value):
	return format_amount(value, False) if value > 0 else "0.00"

@register.filter
def credit(value):
	return format_amount(-value, False) if value < 0 else "0.00"
