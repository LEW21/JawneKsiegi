# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

class Migration(migrations.Migration):

	dependencies = [
		('kw', '0001_initial'),
	]

	sql = [
"""CREATE VIEW kw_event_banktransfer_matches AS
SELECT t.document_ptr_id as t_id, min(r.priority) as r_priority
FROM kw_banktransfer t
JOIN kw_banktransferrule r
	ON t.title like r.match_title
	AND CASE WHEN r.min_amount IS NOT NULL THEN t.amount >= r.min_amount ELSE 1 END
	AND CASE WHEN r.max_amount IS NOT NULL THEN t.amount <= r.max_amount ELSE 1 END
	AND CASE WHEN r.match_contractor_id IS NOT NULL THEN t.contractor_id = r.match_contractor_id ELSE 1 END
GROUP BY t.document_ptr_id;""",

"""CREATE VIEW kw_event_banktransfer AS
SELECT t.document_ptr_id, coalesce(sr.dst_id, e.src_id, t.contractor_id), coalesce(dr.dst_id, e.dst_id, t.contractor_id), abs(t.amount)
FROM kw_event_banktransfer_matches m
LEFT JOIN kw_banktransfer t ON m.t_id = t.document_ptr_id
LEFT JOIN kw_banktransferrule r ON m.r_priority = r.priority
LEFT JOIN kw_banktransferruleevent e ON r.id = e.rule_id
LEFT JOIN kw_accountrelation sr ON e.src_rel_id = sr.type_id AND t.contractor_id = sr.src_id
LEFT JOIN kw_accountrelation dr ON e.dst_rel_id = dr.type_id AND t.contractor_id = dr.src_id;""",

"""CREATE VIEW kw_event_all AS

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
LEFT JOIN kw_account us ON us.text_id = "US"
WHERE i.pit_amount > 0;""",

"""CREATE VIEW kw_event AS
SELECT (((e.doc_id * 1000 + e.src_id) * 1000 + e.dst_id) * 100000 + e.amount) as id, e.doc_id, e.src_id, e.dst_id, e.amount
FROM kw_event_all e
LEFT JOIN kw_document d ON d.id = e.doc_id
ORDER BY d.date ASC, e.doc_id ASC, e.src_id ASC, e.dst_id ASC, e.amount ASC;""",

"""CREATE VIEW kw_turnover AS
SELECT a.id, ifnull(Wn, 0) as debit, ifnull(Ma, 0) as credit, ifnull(Wn, 0)-ifnull(Ma, 0) as balance
FROM kw_account a
LEFT JOIN (
        SELECT k.id as acc, sum(dst.amount) as Wn FROM kw_account k
        LEFT JOIN kw_event dst ON k.id = dst.dst_id
        GROUP BY k.id) wn ON wn.acc = a.id
LEFT JOIN (
        SELECT k.id as acc, sum(src.amount) as Ma FROM kw_account k
        LEFT JOIN kw_event src ON k.id = src.src_id
        GROUP BY k.id) ma ON ma.acc = a.id
ORDER BY id;""",
	]

	operations = [migrations.RunSQL(x) for x in sql]
