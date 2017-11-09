# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.core.validators import MaxValueValidator


class Stores(models.Model):
    store_name = models.CharField(max_length=200, unique=True)
    permanent_token = models.CharField(max_length=200)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.store_name


class StoreSettings(models.Model):
    store_name = models.ForeignKey('Stores', on_delete=models.CASCADE)

    # Look back in minutes. 24 hours by default
    look_back = models.PositiveIntegerField(default=1440, validators=[MaxValueValidator(100), ])


class Product(models.Model):
    store_name = models.ForeignKey('Stores', on_delete=models.CASCADE)
    product_id = models.CharField(max_length=200)
    product_name = models.TextField()

    class Meta:
        unique_together = (('store_name', 'product_id'),)


class Orders(models.Model):
    store_name = models.ForeignKey('Stores', on_delete=models.CASCADE)
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE)
    order_id = models.CharField(max_length=200)
    qty = models.IntegerField(validators=[MaxValueValidator(250), ])

    class Meta:
        unique_together = (('store_name', 'product_id', 'order_id'),)


class Modal(models.Model):
    store_name = models.ForeignKey('Stores', on_delete=models.CASCADE)
    modal_text_id = models.ForeignKey('ModalTextSettings', on_delete=models.CASCADE)
    location = models.CharField(max_length=200)
    color = models.CharField(max_length=200)
    duration = models.IntegerField()

    class Meta:
        unique_together = (('store_name', 'modal_text_id'),)


class ModalTextSettings(models.Model):
    modal_text_id = models.CharField(max_length=200, unique=True)
    modal_text_field = models.TextField()


class ProductViews(models.Model):
    store_name = models.ForeignKey('Stores', on_delete=models.CASCADE)
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE)
    view_count = models.IntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        unique_together = (('store_name', 'product_id'),)
