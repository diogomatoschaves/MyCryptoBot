# Generated by Django 3.2 on 2023-01-25 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0072_auto_20230125_0721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='open_time',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
