import math

from django.db import migrations


def convert_trades_profit_loss(apps, schema_editor):
    Pipeline = apps.get_model('model', 'Pipeline')

    for pipeline in Pipeline.objects.all():
        if pipeline.current_equity is None:
            pipeline.current_equity = pipeline.initial_equity

            pipeline.save()


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0089_auto_20240123_1849'),
    ]

    operations = [
        migrations.RunPython(convert_trades_profit_loss)
    ]
