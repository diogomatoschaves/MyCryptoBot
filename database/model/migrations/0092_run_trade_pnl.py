import math

from django.db import migrations


def get_profit_loss(trade):
    return (trade.close_price - trade.open_price) * trade.amount * trade.side


def get_profit_loss_pct(trade):
    return (math.exp(math.log(trade.close_price / trade.open_price) * trade.side) - 1) * trade.leverage


def convert_trades_profit_loss(apps, schema_editor):
    Trade = apps.get_model('model', 'Trade')

    for trade in Trade.objects.all():
        try:
            trade.pnl = get_profit_loss(trade)
            trade.pnl_pct = get_profit_loss_pct(trade)

            trade.save()
        except TypeError:
            continue


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0091_auto_20240127_0743'),
    ]

    operations = [
        migrations.RunPython(convert_trades_profit_loss)
    ]
