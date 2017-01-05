# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import kw.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('amount', models.IntegerField(verbose_name='amount')),
            ],
            options={
                'verbose_name_plural': 'events',
                'verbose_name': 'event',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('num_id', models.CharField(max_length=30, verbose_name='numeric id')),
                ('text_id', models.CharField(max_length=30, verbose_name='text id')),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('address', models.CharField(max_length=200, verbose_name='address', blank=True)),
                ('bank_account', models.CharField(max_length=200, verbose_name='bank account', blank=True)),
                ('private', models.BooleanField(default=False, verbose_name='private')),
                ('locality', models.CharField(max_length=200, verbose_name='locality', blank=True)),
                ('facebook_id', models.CharField(max_length=50, verbose_name='facebook id', blank=True)),
            ],
            options={
                'verbose_name_plural': 'accounts',
                'ordering': ['num_id'],
                'verbose_name': 'account',
            },
        ),
        migrations.CreateModel(
            name='AccountRelation',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
            ],
            options={
                'verbose_name_plural': 'account relations',
                'verbose_name': 'account relation',
            },
        ),
        migrations.CreateModel(
            name='AccountRelationType',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('text_id', models.CharField(max_length=30, verbose_name='text id')),
            ],
            options={
                'verbose_name_plural': 'account relation types',
                'verbose_name': 'account relation type',
            },
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('file', models.FileField(upload_to=kw.models.upload_to, verbose_name='file')),
                ('public', models.BooleanField(default=True, verbose_name='public')),
            ],
            options={
                'verbose_name_plural': 'attachments',
                'verbose_name': 'attachment',
            },
        ),
        migrations.CreateModel(
            name='BankTransferRule',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('priority', models.IntegerField(unique=True, verbose_name='priority')),
                ('match_title', models.CharField(max_length=200, verbose_name='match title', default='%')),
                ('min_amount', models.IntegerField(verbose_name='min amount', blank=True, null=True)),
                ('max_amount', models.IntegerField(verbose_name='max amount', blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'bank transfer interpretation rules',
                'ordering': ['priority'],
                'verbose_name': 'bank transfer interpretation rule',
            },
        ),
        migrations.CreateModel(
            name='BankTransferRuleEvent',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
            ],
            options={
                'verbose_name_plural': 'generated events',
                'verbose_name': 'generated event',
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('date', models.DateField(verbose_name='date')),
                ('number', models.CharField(max_length=50, verbose_name='number')),
            ],
            options={
                'verbose_name_plural': 'documents',
                'verbose_name': 'document',
            },
        ),
        migrations.CreateModel(
            name='DocumentType',
            fields=[
                ('id', models.CharField(serialize=False, max_length=1, verbose_name='id', primary_key=True)),
                ('name', models.CharField(max_length=30, verbose_name='name')),
            ],
            options={
                'verbose_name_plural': 'document types',
                'verbose_name': 'document type',
            },
        ),
        migrations.CreateModel(
            name='InvoiceLine',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('number', models.IntegerField(verbose_name='number')),
                ('amount', models.IntegerField(verbose_name='amount')),
            ],
            options={
                'verbose_name_plural': 'invoice lines',
                'verbose_name': 'invoice line',
            },
        ),
        migrations.CreateModel(
            name='Turnover',
            fields=[
                ('id', models.OneToOneField(serialize=False, to='kw.Account', verbose_name='account', primary_key=True, related_name='turnover', db_column='id', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('debit', models.IntegerField(verbose_name='debit')),
                ('credit', models.IntegerField(verbose_name='credit')),
                ('balance', models.IntegerField(verbose_name='balance')),
            ],
            options={
                'verbose_name_plural': 'turnovers',
                'verbose_name': 'turnover',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='BankTransfer',
            fields=[
                ('document_ptr', models.OneToOneField(serialize=False, to='kw.Document', parent_link=True, auto_created=True, primary_key=True)),
                ('amount', models.IntegerField(verbose_name='amount')),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('contractor', models.ForeignKey(to='kw.Account', verbose_name='contractor', related_name='foreign_transfers')),
            ],
            options={
                'verbose_name_plural': 'bank transfers',
                'verbose_name': 'bank transfer',
            },
            bases=('kw.document',),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('document_ptr', models.OneToOneField(serialize=False, to='kw.Document', parent_link=True, auto_created=True, primary_key=True)),
                ('pit_amount', models.IntegerField(default=0, verbose_name='PIT amount')),
                ('buyer', models.ForeignKey(to='kw.Account', default=1, related_name='bought', verbose_name='buyer')),
                ('seller', models.ForeignKey(to='kw.Account', verbose_name='seller', related_name='sold')),
            ],
            options={
                'verbose_name_plural': 'invoices',
                'verbose_name': 'invoice',
            },
            bases=('kw.document',),
        ),
        migrations.AddField(
            model_name='invoiceline',
            name='account',
            field=models.ForeignKey(to='kw.Account', verbose_name='account'),
        ),
        migrations.AddField(
            model_name='document',
            name='issuer',
            field=models.ForeignKey(to='kw.Account', verbose_name='issuer', related_name='documents'),
        ),
        migrations.AddField(
            model_name='document',
            name='type',
            field=models.ForeignKey(to='kw.DocumentType', verbose_name='type'),
        ),
        migrations.AddField(
            model_name='banktransferruleevent',
            name='dst',
            field=models.ForeignKey(to='kw.Account', verbose_name='to (preset)', blank=True, related_name='+', null=True),
        ),
        migrations.AddField(
            model_name='banktransferruleevent',
            name='dst_rel',
            field=models.ForeignKey(to='kw.AccountRelationType', verbose_name="to (matched transfer's contractor's rel)", blank=True, related_name='+', null=True),
        ),
        migrations.AddField(
            model_name='banktransferruleevent',
            name='rule',
            field=models.ForeignKey(to='kw.BankTransferRule', verbose_name='rule', related_name='events'),
        ),
        migrations.AddField(
            model_name='banktransferruleevent',
            name='src',
            field=models.ForeignKey(to='kw.Account', verbose_name='from (preset)', blank=True, related_name='+', null=True),
        ),
        migrations.AddField(
            model_name='banktransferruleevent',
            name='src_rel',
            field=models.ForeignKey(to='kw.AccountRelationType', verbose_name="from (matched transfer's contractor's rel)", blank=True, related_name='+', null=True),
        ),
        migrations.AddField(
            model_name='banktransferrule',
            name='match_contractor',
            field=models.ForeignKey(to='kw.Account', verbose_name='match contractor', blank=True, related_name='+', null=True),
        ),
        migrations.AddField(
            model_name='attachment',
            name='doc',
            field=models.ForeignKey(to='kw.Document', verbose_name='document', related_name='files'),
        ),
        migrations.AddField(
            model_name='accountrelation',
            name='dst',
            field=models.ForeignKey(to='kw.Account', verbose_name='to', related_name='relations_to'),
        ),
        migrations.AddField(
            model_name='accountrelation',
            name='src',
            field=models.ForeignKey(to='kw.Account', verbose_name='from', related_name='relations_from'),
        ),
        migrations.AddField(
            model_name='accountrelation',
            name='type',
            field=models.ForeignKey(to='kw.AccountRelationType', verbose_name='type'),
        ),
        migrations.AddField(
            model_name='invoiceline',
            name='invoice',
            field=models.ForeignKey(to='kw.Invoice', verbose_name='invoice', related_name='lines'),
        ),
    ]
