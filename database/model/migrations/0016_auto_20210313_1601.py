# Generated by Django 2.2.5 on 2021-03-13 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0015_messariapi'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messariapi',
            name='volume',
            field=models.FloatField(null=True),
        ),
    ]