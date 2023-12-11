from django.db import migrations


def convert_strategies(apps, schema_editor):
    Pipeline = apps.get_model('model', 'Pipeline')
    Strategy = apps.get_model('model', 'Strategy')

    for pipeline in Pipeline.objects.all():
        strategy_name = pipeline.strategy
        strategy_params = pipeline.params

        strategy_obj = Strategy.objects.create(name=strategy_name, params=strategy_params)

        pipeline.strategies.add(strategy_obj)
        pipeline.save()


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0083_add_strategy_model'),
    ]

    operations = [
        migrations.RunPython(convert_strategies)
    ]
