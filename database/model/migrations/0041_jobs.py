# Generated by Django 3.1.7 on 2021-04-09 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0033_structureddata'),
    ]

    operations = [
        migrations.CreateModel(
            name='Jobs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_id', models.TextField()),
                ('app', models.TextField()),
            ],
            options={
                'unique_together': {('job_id', 'app')},
            },
        ),
    ]
