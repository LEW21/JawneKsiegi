from django import template
import locale

register = template.Library()

def format_amount(amount, add_sign = True):
	if not isinstance(amount, int):
		return ''
	sign = 1 if amount > 0 else -1 if amount < 0 else 0
	abs_amount = amount if sign >= 0 else -amount
	return ("+" if sign > 0 and add_sign else "-" if sign < 0 else "") + locale.format_string('%.2f', abs_amount/100, grouping=True, monetary=True)

@register.filter
def money(value):
	return format_amount(value, False)

@register.filter
def money_sign(value):
	return format_amount(value, True)

@register.filter
def money_wnma(value):
	return format_amount(value, True).replace('+', 'Wn ').replace('-', 'Ma ')

@register.filter
def debit(value):
	return format_amount(value, False) if value > 0 else "0.00"

@register.filter
def credit(value):
	return format_amount(-value, False) if value < 0 else "0.00"
