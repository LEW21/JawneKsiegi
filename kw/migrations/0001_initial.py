# Generated by Django 2.2.25 on 2021-12-23 18:35

from django.db import migrations, models
import django.db.models.deletion
import kw.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(verbose_name='amount')),
            ],
            options={
                'verbose_name': 'event',
                'verbose_name_plural': 'events',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_id', models.CharField(max_length=30, verbose_name='numeric id')),
                ('shortcut', models.CharField(blank=True, max_length=30, verbose_name='shortcut')),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('address', models.CharField(blank=True, max_length=200, verbose_name='address')),
                ('bank_account', models.CharField(blank=True, max_length=200, verbose_name='bank account')),
                ('locality', models.CharField(blank=True, max_length=200, verbose_name='locality')),
                ('facebook_id', models.CharField(blank=True, max_length=50, verbose_name='facebook id')),
                ('name_public', models.BooleanField(default=True, verbose_name='publish name?')),
                ('locality_public', models.BooleanField(default=True, verbose_name='publish locality?')),
                ('address_public', models.BooleanField(default=False, verbose_name='publish address?')),
                ('bank_account_public', models.BooleanField(default=False, verbose_name='publish bank account?')),
                ('facebook_public', models.BooleanField(default=True, verbose_name='publish facebook?')),
            ],
            options={
                'verbose_name': 'account',
                'verbose_name_plural': 'accounts',
                'ordering': ['num_id'],
            },
        ),
        migrations.CreateModel(
            name='AccountRelationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_id', models.CharField(max_length=30, verbose_name='text id')),
            ],
            options={
                'verbose_name': 'account relation type',
                'verbose_name_plural': 'account relation types',
            },
        ),
        migrations.CreateModel(
            name='BankTransferRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.IntegerField(unique=True, verbose_name='priority')),
                ('match_title', models.CharField(default='%', max_length=200, verbose_name='match title')),
                ('min_amount', models.IntegerField(blank=True, null=True, verbose_name='min amount')),
                ('max_amount', models.IntegerField(blank=True, null=True, verbose_name='max amount')),
                ('match_contractor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='kw.Account', verbose_name='match contractor')),
            ],
            options={
                'verbose_name': 'bank transfer interpretation rule',
                'verbose_name_plural': 'bank transfer interpretation rules',
                'ordering': ['priority'],
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='date')),
                ('date_posted', models.DateField(auto_now_add=True, verbose_name='date posted')),
                ('number', models.CharField(max_length=50, verbose_name='number')),
                ('issuer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='kw.Account', verbose_name='issuer')),
            ],
            options={
                'verbose_name': 'document',
                'verbose_name_plural': 'documents',
                'ordering': ('issuer', 'number'),
            },
        ),
        migrations.CreateModel(
            name='DocumentType',
            fields=[
                ('id', models.CharField(max_length=1, primary_key=True, serialize=False, verbose_name='id')),
                ('name', models.CharField(max_length=30, verbose_name='name')),
            ],
            options={
                'verbose_name': 'document type',
                'verbose_name_plural': 'document types',
            },
        ),
        migrations.CreateModel(
            name='Turnover',
            fields=[
                ('id', models.OneToOneField(db_column='id', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, related_name='turnover', serialize=False, to='kw.Account', verbose_name='account')),
                ('debit', models.IntegerField(verbose_name='debit')),
                ('credit', models.IntegerField(verbose_name='credit')),
                ('balance', models.IntegerField(verbose_name='balance')),
            ],
            options={
                'verbose_name': 'turnover',
                'verbose_name_plural': 'turnovers',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('document_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='kw.Document')),
                ('date_of_sale', models.DateField(verbose_name='date of sale')),
                ('pit_amount', models.IntegerField(default=0, verbose_name='PIT amount')),
                ('buyer', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='bought', to='kw.Account', verbose_name='buyer')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sold', to='kw.Account', verbose_name='seller')),
            ],
            options={
                'verbose_name': 'invoice',
                'verbose_name_plural': 'invoices',
            },
            bases=('kw.document',),
        ),
        migrations.AddField(
            model_name='document',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='kw.DocumentType', verbose_name='type'),
        ),
        migrations.CreateModel(
            name='BankTransferRuleEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dst', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='kw.Account', verbose_name='to (preset)')),
                ('dst_rel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='kw.AccountRelationType', verbose_name="to (matched transfer's contractor's rel)")),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='kw.BankTransferRule', verbose_name='rule')),
                ('src', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='kw.Account', verbose_name='from (preset)')),
                ('src_rel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='kw.AccountRelationType', verbose_name="from (matched transfer's contractor's rel)")),
            ],
            options={
                'verbose_name': 'generated event',
                'verbose_name_plural': 'generated events',
            },
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('file', models.FileField(upload_to=kw.models.upload_to, verbose_name='file')),
                ('public', models.BooleanField(default=True, verbose_name='public')),
                ('doc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='kw.Document', verbose_name='document')),
            ],
            options={
                'verbose_name': 'attachment',
                'verbose_name_plural': 'attachments',
            },
        ),
        migrations.CreateModel(
            name='AccountRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dst', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relations_to', to='kw.Account', verbose_name='to')),
                ('src', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relations_from', to='kw.Account', verbose_name='from')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='kw.AccountRelationType', verbose_name='type')),
            ],
            options={
                'verbose_name': 'account relation',
                'verbose_name_plural': 'account relations',
            },
        ),
        migrations.CreateModel(
            name='InvoiceLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(verbose_name='number')),
                ('amount', models.IntegerField(verbose_name='amount')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='kw.Account', verbose_name='account')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='kw.Invoice', verbose_name='invoice')),
            ],
            options={
                'verbose_name': 'invoice line',
                'verbose_name_plural': 'invoice lines',
            },
        ),
        migrations.AlterUniqueTogether(
            name='document',
            unique_together={('issuer', 'number')},
        ),
        migrations.CreateModel(
            name='BankTransfer',
            fields=[
                ('document_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='kw.Document')),
                ('amount', models.IntegerField(verbose_name='amount')),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('contractor', models.ForeignKey(limit_choices_to=models.Q(_negated=True, num_id__startswith=4), on_delete=django.db.models.deletion.CASCADE, related_name='foreign_transfers', to='kw.Account', verbose_name='contractor')),
            ],
            options={
                'verbose_name': 'bank transfer',
                'verbose_name_plural': 'bank transfers',
            },
            bases=('kw.document',),
        ),
    ]
