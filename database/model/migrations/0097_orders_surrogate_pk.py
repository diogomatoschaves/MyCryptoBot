from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0096_auto_20260612_0813'),
    ]

    operations = [
        # drop the global primary key on order_id (Binance order ids are only
        # unique per symbol, and collide between live and testnet/mock)
        migrations.AlterField(
            model_name='orders',
            name='order_id',
            field=models.TextField(),
        ),
        # introduce a surrogate auto primary key
        migrations.AddField(
            model_name='orders',
            name='id',
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
            ),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='orders',
            unique_together={('order_id', 'symbol', 'mock')},
        ),
    ]
