import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Count


def dedup_positions(apps, schema_editor):
    # collapse any pre-existing duplicate positions to one per pipeline
    # (keep the most recent) so the unique constraint can be applied
    Position = apps.get_model('model', 'Position')

    duplicate_pipelines = (
        Position.objects.values('pipeline')
        .annotate(count=Count('id'))
        .filter(count__gt=1)
        .values_list('pipeline', flat=True)
    )

    for pipeline_id in duplicate_pipelines:
        extra = Position.objects.filter(pipeline_id=pipeline_id).order_by('-open_time', '-id')[1:]
        Position.objects.filter(id__in=[p.id for p in extra]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0097_orders_surrogate_pk'),
    ]

    operations = [
        migrations.RunPython(dedup_positions, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='position',
            name='pipeline',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to='model.pipeline', unique=True
            ),
        ),
    ]
