# Generated by Django 2.2.5 on 2021-03-19 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0024_exchangedata_symbol'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchangedata',
            name='name',
            field=models.TextField(default='binance'),
            preserve_default=False,
        ),
    ]