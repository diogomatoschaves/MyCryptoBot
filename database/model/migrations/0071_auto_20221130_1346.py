# Generated by Django 3.1.7 on 2022-11-30 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0070_auto_20221130_1331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.TextField(max_length=255, unique=True, verbose_name='username'),
        ),
    ]