# Generated by Django 3.1.7 on 2021-04-09 11:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0034_auto_20210409_0617'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messariapi',
            name='asset',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='model.asset'),
        ),
    ]
