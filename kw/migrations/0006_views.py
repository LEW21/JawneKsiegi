from django.db import models, migrations

class Migration(migrations.Migration):

	dependencies = [
		('kw', '0005_event'),
	]

	sql = [
"""CREATE VIEW kw_turnover AS
SELECT a.id, coalesce(Wn, 0) as debit, coalesce(Ma, 0) as credit, coalesce(Wn, 0)-coalesce(Ma, 0) as balance
FROM kw_account a
LEFT JOIN (
		SELECT k.id as acc, sum(dst.amount) as Wn FROM kw_account k
		LEFT JOIN kw_account sub ON (sub.id = k.id OR sub.num_id LIKE k.num_id||'-%')
		LEFT JOIN kw_event dst ON sub.id = dst.dst_id
		GROUP BY k.id) wn ON wn.acc = a.id
LEFT JOIN (
		SELECT k.id as acc, sum(src.amount) as Ma FROM kw_account k
		LEFT JOIN kw_account sub ON (sub.id = k.id OR sub.num_id LIKE k.num_id||'-%')
		LEFT JOIN kw_event src ON sub.id = src.src_id
		GROUP BY k.id) ma ON ma.acc = a.id
ORDER BY id;""",
	]

	operations = [migrations.RunSQL(x) for x in sql]
