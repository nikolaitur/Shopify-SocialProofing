# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-25 19:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20171125_0019'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='modal',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='modal',
            name='modal_text_settings',
        ),
        migrations.DeleteModel(
            name='ModalTextSettings',
        ),
    ]