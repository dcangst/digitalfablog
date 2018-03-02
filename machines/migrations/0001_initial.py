# Generated by Django 2.0.1 on 2018-03-02 13:58

import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='machine name', max_length=255, verbose_name='Name')),
                ('abbreviation', models.CharField(default='?', help_text='Abbreviation shown in overviews', max_length=5, verbose_name='Abbreviation')),
                ('color', models.CharField(default='#212529', help_text='Color used in Overview. Any CSS syntax will work.', max_length=30, verbose_name='Overview color')),
                ('unit', models.DurationField(default=datetime.timedelta(0, 1800), help_text='unit', verbose_name='unit')),
                ('price_per_unit', models.DecimalField(decimal_places=2, help_text='price per unit', max_digits=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='price/unit')),
            ],
            options={
                'verbose_name': 'machine',
                'verbose_name_plural': 'machines',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='MachineStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(help_text='Machine status start', verbose_name='start time')),
                ('end_time', models.DateTimeField(blank=True, help_text='Machine status end time', null=True, verbose_name='end time')),
                ('details', models.CharField(blank=True, help_text='Details concerning the machine status', max_length=300, null=True, verbose_name='details')),
                ('machine', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='machines.Machine')),
            ],
            options={
                'verbose_name': 'Machine Satus',
                'verbose_name_plural': 'Machine Statuses',
                'ordering': ['-start_time'],
            },
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('severity', models.PositiveSmallIntegerField(default=0, help_text='severity of status', verbose_name='severity')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
            ],
            options={
                'verbose_name': 'Status',
                'verbose_name_plural': 'Statuses',
            },
        ),
        migrations.AddField(
            model_name='machinestatus',
            name='status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='machines.Status', verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='machine',
            name='status',
            field=models.ManyToManyField(through='machines.MachineStatus', to='machines.Status', verbose_name='machine status'),
        ),
    ]
