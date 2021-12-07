# Generated by Django 3.1.7 on 2021-12-06 11:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0046_orders_cummulative_quote_qty'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orders',
            name='id',
        ),
        migrations.AddField(
            model_name='orders',
            name='exchange',
            field=models.ForeignKey(default='binance', on_delete=django.db.models.deletion.SET_DEFAULT, to='model.exchange'),
        ),
        migrations.AlterField(
            model_name='orders',
            name='order_id',
            field=models.IntegerField(default=1, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Pipeline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interval', models.TextField()),
                ('strategy', models.TextField(choices=[('BollingerBands', 'Bollinger Bands'), ('MachineLearning', 'Machine Learning'), ('Momentum', 'Momentum'), ('MovingAverageConvergenceDivergence', 'Moving Average Convergence Divergence'), ('MovingAverage', 'Moving Average'), ('MovingAverageCrossover', 'Moving Average Crossover')])),
                ('exchange', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='model.exchange')),
                ('symbol', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='model.symbol')),
            ],
        ),
    ]
