# Generated by Django 2.2.5 on 2021-03-10 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0012_auto_20210310_0544'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='name',
            field=models.TextField(null=True),
        ),
    ]
