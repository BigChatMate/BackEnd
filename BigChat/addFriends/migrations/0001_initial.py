# Generated by Django 2.1.2 on 2018-11-16 07:03

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='chatMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('member_id', django.contrib.postgres.fields.ArrayField(base_field=models.BigIntegerField(), size=None)),
                ('date_added', models.DateTimeField(auto_now=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'chat_members',
            },
        ),
        migrations.CreateModel(
            name='FriendRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=255, unique=True)),
                ('friend_requests_emails_sent', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255, unique=True), null=True, size=None)),
                ('friend_requests_emails_recieved', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255, unique=True), null=True, size=None)),
            ],
            options={
                'db_table': 'friend_requests',
            },
        ),
    ]
