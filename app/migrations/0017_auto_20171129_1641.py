# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-29 16:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_product_handle'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='collection_id',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='product',
            name='product_type',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='product',
            name='tags',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='product',
            name='vendor',
            field=models.TextField(default=''),
        ),
    ]
