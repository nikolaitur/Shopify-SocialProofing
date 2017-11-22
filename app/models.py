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

    # Look back in minutes. 24 hours by default. Max 31 Days
    look_back = models.PositiveIntegerField(default=1440, validators=[MaxValueValidator(44640), ])


class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

    product_id = models.CharField(max_length=200)
    product_name = models.TextField()

    class Meta:
        unique_together = (('store', 'product_id'),)


class Orders(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    order_id = models.CharField(max_length=200)
    qty = models.IntegerField(validators=[MaxValueValidator(250), ])
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = (('store', 'product', 'order_id'),)


class ModalTextSettings(models.Model):
    modal_text_id = models.CharField(max_length=200, unique=True)
    modal_text_field = models.TextField()


class Modal(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    modal_text_settings = models.ForeignKey(ModalTextSettings, on_delete=models.CASCADE)
    location = models.CharField(max_length=200)
    color = models.CharField(max_length=200)
    duration = models.IntegerField()

    class Meta:
        unique_together = (('store', 'modal_text_settings'),)


class ProductViews(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    view_count = models.IntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        unique_together = (('store', 'product'),)
