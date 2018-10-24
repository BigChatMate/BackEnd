# Generated by Django 2.1.2 on 2018-10-24 23:32

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChatList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.BigIntegerField()),
                ('chat_id', models.TextField(default='')),
                ('message', models.TextField(default='')),
                ('message_type', models.IntegerField(blank=True)),
                ('flag', models.IntegerField(blank=True)),
                ('date_added', models.DateTimeField()),
                ('date_modified', models.DateTimeField()),
                ('name', models.TextField()),
            ],
            options={
                'db_table': 'chat_list',
            },
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('email', models.CharField(max_length=100, unique=True, validators=[django.core.validators.EmailValidator()])),
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('token', models.CharField(max_length=255, unique=True)),
                ('chat_list_id', models.TextField(default='')),
            ],
            options={
                'db_table': 'myAuth_users',
            },
        ),
    ]
