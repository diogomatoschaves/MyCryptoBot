# Generated by Django 2.2.5 on 2021-03-15 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0022_auto_20210315_0956'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='market_cap_ranking',
            field=models.IntegerField(null=True),
        ),
    ]
