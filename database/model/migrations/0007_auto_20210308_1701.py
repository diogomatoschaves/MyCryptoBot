# Generated by Django 2.2.5 on 2021-03-08 23:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0006_auto_20210308_1654'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lunarcrushtimeentries',
            old_name='tweet_favourites',
            new_name='tweet_favorites',
        ),
    ]