# Generated by Django 3.2 on 2021-04-15 15:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0043_auto_20210411_0918'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='token_is_treasury_decentralized',
            field=models.BooleanField(null=True),
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.IntegerField(null=True)),
                ('client_order_id', models.TextField(null=True)),
                ('transact_time', models.DateTimeField()),
                ('price', models.FloatField()),
                ('original_qty', models.FloatField()),
                ('executed_qty', models.FloatField()),
                ('status', models.TextField()),
                ('type', models.TextField()),
                ('side', models.TextField()),
                ('is_isolated', models.BooleanField(default=False)),
                ('mock', models.BooleanField(default=False, null=True)),
                ('symbol', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='model.symbol')),
            ],
        ),
    ]
