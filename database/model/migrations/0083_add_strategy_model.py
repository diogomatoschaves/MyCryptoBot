import json

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0082_rename_allocation_pipeline_equity'),
    ]

    operations = [
        migrations.CreateModel(
            name='Strategy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('params', models.TextField(blank=True, default=json.dumps('{}'))),
            ],
        ),
        migrations.AddField(
            model_name='pipeline',
            name='strategies',
            field=models.ManyToManyField(to='model.Strategy'),
        ),
    ]
