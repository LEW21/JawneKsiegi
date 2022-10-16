from django.contrib import admin
from .models import *

class AccountRelationInline(admin.TabularInline):
	model = AccountRelation
	extra = 0
	fk_name = "src"

class InvoiceLineInline(admin.TabularInline):
	model = InvoiceLine
	extra = 0

class AttachmentInline(admin.TabularInline):
	model = Attachment
	extra = 0

class AccountAdmin(admin.ModelAdmin):
	list_display = ('num_id', 'shortcut', 'name', 'name_public', 'locality', 'locality_public', 'address', 'address_public', 'bank_account', 'bank_account_public')
	list_editable = ('shortcut', 'name', 'name_public', 'locality', 'locality_public', 'address', 'address_public', 'bank_account', 'bank_account_public')
	inlines = [
		AccountRelationInline,
	]

class InvoiceAdmin(admin.ModelAdmin):
	list_display = ('__str__', 'date', 'amount')
	date_hierarchy = 'date'
	radio_fields = {"type": admin.HORIZONTAL}
	inlines = [
		InvoiceLineInline,
		AttachmentInline,
	]

class BankTransferAdmin(admin.ModelAdmin):
	list_display = ('__str__', 'date', 'amount', 'title')
	date_hierarchy = 'date'
	inlines = [
		AttachmentInline,
	]

admin.site.register(Account, AccountAdmin)
admin.site.register(AccountRelationType)
admin.site.register(DocumentType)
admin.site.register(BankTransfer, BankTransferAdmin)
admin.site.register(Invoice, InvoiceAdmin)
