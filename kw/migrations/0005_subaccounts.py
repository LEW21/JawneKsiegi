# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

	dependencies = [
		('kw', '0004_auto_20150829_1234'),
	]

	sql = [
		"DROP VIEW kw_turnover",

"""CREATE VIEW kw_turnover AS
SELECT a.id, ifnull(Wn, 0) as debit, ifnull(Ma, 0) as credit, ifnull(Wn, 0)-ifnull(Ma, 0) as balance
FROM kw_account a
LEFT JOIN (
		SELECT k.id as acc, sum(dst.amount) as Wn FROM kw_account k
		LEFT JOIN kw_account sub ON (sub.id = k.id OR sub.num_id LIKE k.num_id||"-%")
		LEFT JOIN kw_event dst ON sub.id = dst.dst_id
		GROUP BY k.id) wn ON wn.acc = a.id
LEFT JOIN (
		SELECT k.id as acc, sum(src.amount) as Ma FROM kw_account k
		LEFT JOIN kw_account sub ON (sub.id = k.id OR sub.num_id LIKE k.num_id||"-%")
		LEFT JOIN kw_event src ON sub.id = src.src_id
		GROUP BY k.id) ma ON ma.acc = a.id
ORDER BY id;""",
	]

	operations = [migrations.RunSQL(x) for x in sql]
