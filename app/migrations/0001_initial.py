# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-10-31 19:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Stores',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_name', models.CharField(max_length=200)),
                ('permanent_token', models.CharField(max_length=200)),
            ],
        ),
    ]