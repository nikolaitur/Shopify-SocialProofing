# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models


class Stores(models.Model):
    store_name = models.CharField(max_length=200)
    permanent_token = models.CharField(max_length=200)

    def __str__(self):
        return self.store_name
