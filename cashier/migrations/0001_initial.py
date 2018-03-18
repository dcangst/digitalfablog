# Generated by Django 2.0.3 on 2018-03-18 09:05

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, help_text='Booking date and time', verbose_name='Date & Time')),
                ('amount', models.DecimalField(decimal_places=2, help_text='Amount of the booking', max_digits=10, verbose_name='amount')),
                ('comment', models.CharField(blank=True, help_text='Comment on Booking', max_length=255, verbose_name='comment')),
            ],
            options={
                'verbose_name': 'Booking',
                'verbose_name_plural': 'Bookings',
                'ordering': ['timestamp'],
                'permissions': (('view_bookings', 'Can view bookings'),),
            },
        ),
        migrations.CreateModel(
            name='BookingType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purpose', models.PositiveSmallIntegerField(choices=[(0, 'Fablog'), (1, 'Donation'), (2, 'Store'), (3, 'Expenses'), (4, 'Correction'), (5, 'Membership')], default=0, unique=True)),
                ('description', models.CharField(blank=True, help_text='Description of Booking Type', max_length=250, verbose_name='description')),
            ],
            options={
                'verbose_name': 'booking type',
                'verbose_name_plural': 'booking types',
                'permissions': (('view_account', 'Can view booking types'),),
            },
        ),
        migrations.CreateModel(
            name='CashCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Creation date and time', verbose_name='created at')),
                ('cashier_date', models.DateTimeField(default=django.utils.timezone.now, help_text='Cash account creation date and time', verbose_name='cash account date')),
            ],
            options={
                'verbose_name': 'cash count',
                'verbose_name_plural': 'cash counts',
                'ordering': ['-cashier_date', '-created_at'],
                'permissions': (('view_cash_counts', 'Can view cash counts'),),
            },
        ),
        migrations.CreateModel(
            name='CashCountNominal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.PositiveSmallIntegerField(help_text='Count of None', verbose_name='count')),
                ('cash_count', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cashier.CashCount')),
            ],
            options={
                'verbose_name': 'Cash count nominal',
                'verbose_name_plural': 'Cash count nominals',
                'permissions': (('view_cash_count_nominals', 'Can view cash count nominals'),),
            },
        ),
        migrations.CreateModel(
            name='CashNominal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, help_text='Value of denomination', max_digits=7, verbose_name='value')),
            ],
            options={
                'verbose_name': 'Cash nominal',
                'verbose_name_plural': 'Cash nominals',
                'ordering': ['value'],
                'permissions': (('view_cash_nominals', 'Can view cash nominals'),),
            },
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of currency', max_length=20, unique=True, verbose_name='currency name')),
                ('fractional_name', models.CharField(help_text='Name of fractional currency', max_length=20, unique=True, verbose_name='fractional currency name')),
                ('abbreviation', models.CharField(help_text='Abbreviation of currency', max_length=3, unique=True, verbose_name='currency abbreviation')),
                ('default_currency', models.BooleanField(default=False, help_text='Is this the default currency?', verbose_name='default currency')),
            ],
            options={
                'verbose_name': 'currency',
                'verbose_name_plural': 'currencies',
                'permissions': (('view_currencies', 'Can view currencies'),),
            },
        ),
        migrations.CreateModel(
            name='FinancialAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the account', max_length=20, unique=True, verbose_name='account name')),
                ('default_account', models.BooleanField(default=False, help_text='Is this the default account for which bookings should be made?', verbose_name='default account')),
            ],
            options={
                'verbose_name': 'Financial Account',
                'verbose_name_plural': 'Financial Accounts',
                'permissions': (('view_account', 'Can view account'),),
            },
        ),
        migrations.CreateModel(
            name='FinancialAccountBalance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, help_text='Balance', max_digits=20, verbose_name='balance')),
                ('financial_account', models.ForeignKey(help_text='Associated account', on_delete=django.db.models.deletion.PROTECT, related_name='balances', to='cashier.FinancialAccount', verbose_name='account')),
            ],
            options={
                'verbose_name': 'Account Balance',
                'verbose_name_plural': 'Account Balances',
                'permissions': (('view_account_balance', 'Can view account balances'),),
            },
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(help_text='Three letter short name for display.', max_length=3, verbose_name='short name')),
                ('long_name', models.CharField(help_text='Long name of payment method', max_length=50, verbose_name='long name')),
                ('selectable', models.BooleanField(default=True, help_text='Used to restrict Select Widgets in Forms', verbose_name='Selectable')),
                ('to_account', models.ForeignKey(blank=True, help_text='Account for this payment method', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payment_methods', to='cashier.FinancialAccount', verbose_name='Booking to account')),
            ],
            options={
                'verbose_name': 'payment method',
                'verbose_name_plural': 'payment methods',
                'permissions': (('view_payment_methods', 'Can view payment methods'),),
            },
        ),
        migrations.AddField(
            model_name='cashnominal',
            name='currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='nominals', to='cashier.Currency'),
        ),
        migrations.AddField(
            model_name='cashcountnominal',
            name='cash_nominal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cashier.CashNominal'),
        ),
        migrations.AddField(
            model_name='cashcount',
            name='cash',
            field=models.ManyToManyField(through='cashier.CashCountNominal', to='cashier.CashNominal', verbose_name='Cash'),
        ),
    ]
