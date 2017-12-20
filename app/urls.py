"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^install/?$', views.install, name='install'),
    url(r'^store_settings/?$', views.store_settings, name='store_settings'),
    url(r'^auth/callback/?$', views.auth_callback, name='auth_callback'),
    url(r'^api/store_settings/(?P<store_name>[a-zA-Z0-9_.-]*)/?$', views.store_settings_api, name='store_settings_api'),
    url(r'^api/orders/(?P<store_name>[a-zA-Z0-9_.-]*)/?$', views.orders_api, name='orders_api'),
    url(r'^api/products/(?P<store_name>[a-zA-Z0-9_.-]*)/?$', views.products_api, name='products_api'),
    url(r'^api/modal/(?P<store_name>[a-zA-Z0-9_.-]*)/(?P<product_id>[0-9]*)/?$',
        views.modal_api, name='modal_api'),
    url(r'^api/related/(?P<store_name>[a-zA-Z0-9_.-]*)/(?P<product_id>[0-9]*)/?$',
        views.related_products_api, name='related_products_api'),
    url(r'^api/modal_metrics/?$', views.modal_metrics_api, name='modal_metrics_api'),
    url(r'^webhooks/?$', views.webhooks, name='webhooks'),
]
