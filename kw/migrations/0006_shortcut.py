# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

	dependencies = [
		('kw', '0005_subaccounts'),
	]

	operations = [
		migrations.RenameField(
			model_name='account',
			old_name='text_id',
			new_name='shortcut',
		),
		migrations.AlterField(
			model_name='account',
			name='shortcut',
			field=models.CharField(verbose_name='shortcut', max_length=30, blank=True),
		),
		migrations.RunSQL("""UPDATE kw_account SET shortcut = "" WHERE shortcut = num_id"""),
		migrations.RunSQL("""DROP VIEW kw_event_all"""),
		migrations.RunSQL("""CREATE VIEW kw_event_all AS

SELECT d.id as doc_id, t.contractor_id as src_id, d.issuer_id as dst_id, t.amount
FROM kw_banktransfer t
LEFT JOIN kw_document d ON t.document_ptr_id = d.id
WHERE t.amount > 0

UNION ALL

SELECT d.id, d.issuer_id as src_id, t.contractor_id as dst_id, -t.amount
FROM kw_banktransfer t
LEFT JOIN kw_document d ON t.document_ptr_id = d.id
WHERE t.amount < 0

UNION ALL

SELECT * FROM kw_event_banktransfer

UNION ALL

SELECT i.document_ptr_id, i.seller_id, l.account_id, l.amount
FROM kw_invoiceline l
LEFT JOIN kw_invoice i ON l.invoice_id = i.document_ptr_id

UNION ALL

SELECT i.document_ptr_id, us.id, i.seller_id, i.pit_amount
FROM kw_invoice i
LEFT JOIN kw_account us ON shortcut = "US"
WHERE i.pit_amount > 0;""")
	]
