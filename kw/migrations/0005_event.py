# Generated by Django 4.0 on 2022-10-13 09:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kw', '0004_delete_event'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('amount', models.IntegerField(verbose_name='amount')),
                ('doc', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='events', to='kw.document', verbose_name='document')),
                ('dst', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='events_to', to='kw.account', verbose_name='to')),
                ('src', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='events_from', to='kw.account', verbose_name='from')),
            ],
            options={
                'verbose_name': 'event',
                'verbose_name_plural': 'events',
            },
        ),
    ]