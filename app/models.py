# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.core.validators import MaxValueValidator
from datetime import datetime


class Store(models.Model):
    store_name = models.CharField(max_length=200, unique=True)
    permanent_token = models.CharField(max_length=200)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.store_name


class StoreSettings(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

    # Look back in hours. 24 hours by default. Max 31 Days
    look_back = models.PositiveIntegerField(default=24, validators=[MaxValueValidator(744), ])


class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

    product_id = models.CharField(max_length=200)
    product_name = models.TextField()
    main_image_url = models.TextField(default='')

    class Meta:
        unique_together = (('store', 'product_id'),)


class Orders(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    order_id = models.CharField(max_length=200)
    qty = models.IntegerField(validators=[MaxValueValidator(250), ])
    processed_at = models.DateTimeField(null=True, blank=True)
    first_name = models.TextField(default='')
    last_name = models.TextField(default='')
    province_code = models.TextField(default='')
    country_code = models.TextField(default='')

    class Meta:
        unique_together = (('store', 'product', 'order_id'),)


class Modal(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

    location = models.CharField(max_length=200, default='bottom-right')
    color_hue = models.FloatField(default=83.28)
    color_saturation = models.FloatField(default=0.306)
    color_brightness = models.FloatField(default=0.487)
    social_setting = models.TextField(default='latest')
    size = models.TextField(default='250,100')  # Modal size (wxh)


class APIMetrics(models.Model):
    view = models.TextField()
    snapshot_date = models.DateField(null=True, blank=True)
    view_count = models.IntegerField()
    method = models.TextField(default=0)

    class Meta:
        unique_together = (('snapshot_date', 'view', 'method'),)