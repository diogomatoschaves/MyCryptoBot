# Generated by Django 3.1.7 on 2021-04-09 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0033_structureddata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messariapi',
            name='asset',
            field=models.TextField(null=True),
        ),
    ]