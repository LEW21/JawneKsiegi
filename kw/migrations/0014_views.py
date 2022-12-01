from django.db import models, migrations

class Migration(migrations.Migration):

	dependencies = [
		('kw', '0014_remove_account_metadata'),
	]

	sql = [
"""CREATE VIEW kw_turnover_own AS
SELECT a.id, a.num_id, coalesce(debit, 0) as debit, coalesce(credit, 0) as credit, coalesce(debit, 0)-coalesce(credit, 0) as balance
FROM kw_account a
LEFT JOIN (
		SELECT k.id as acc, sum(dst.amount) as debit FROM kw_account k
		LEFT JOIN kw_event dst ON k.id = dst.dst_id AND dst.date < date()
		GROUP BY k.id) wn ON wn.acc = a.id
LEFT JOIN (
		SELECT k.id as acc, sum(src.amount) as credit FROM kw_account k
		LEFT JOIN kw_event src ON k.id = src.src_id AND src.date < date()
		GROUP BY k.id) ma ON ma.acc = a.id
ORDER BY id;""",
"""CREATE VIEW kw_turnover AS
SELECT a.id, a.num_id, coalesce(sum(sub.debit), 0) as debit, coalesce(sum(sub.credit), 0) as credit, coalesce(sum(max(sub.balance, 0)), 0) as debit_balance, -coalesce(sum(min(sub.balance, 0)), 0) as credit_balance
FROM kw_account a
LEFT JOIN kw_turnover_own sub ON (sub.num_id = a.num_id OR sub.num_id LIKE a.num_id||'-%')
GROUP BY a.id
ORDER BY a.num_id;""",
	]

	operations = [migrations.RunSQL(x) for x in sql]
