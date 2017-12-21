import logging
import re
from urllib.parse import urlparse

import shopify
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.template import loader
from django.views.decorators.clickjacking import xframe_options_exempt
from django.db.models import Sum

from .utils import authenticate, parse_params, find_products_from_social_scope
from .decorators import shop_login_required, api_authentication, track_statistics
from .models import Store, StoreSettings, Modal, Orders, Product, Collection, ModalMetrics, Webhooks
from django.core import serializers
from datetime import date
from django.utils import timezone
from datetime import timedelta
from random import choice
from .shopifyutils import ingest_products, ingest_orders, create_webhook
from .scripts.add_scripttag import add_script
from django.conf import settings
from slacker_log_handler import SlackerLogHandler

slack_handler = SlackerLogHandler(settings.SLACK_API_KEY, 'production-logs', stack_trace=True)

logger = logging.getLogger(__name__)

if settings.DEVELOPMENT_MODE == 'PRODUCTION':
    logger.addHandler(slack_handler)


@track_statistics
def install(request):
    """
    Redirect user to the shopify page to authenticate our app.
    Example request from: https://mystore.myshopify.com
    """
    try:
        shopify.Session.setup(api_key=settings.API_KEY, secret=settings.API_SECRET)
        shop = urlparse(request.build_absolute_uri())[1]
        session = shopify.Session(shop)
        permission_url = session.create_permission_url(scope=settings.SHOPIFY_API_SCOPE,
                                                       redirect_uri=settings.SHOPIFY_AUTH_CALLBACK_URL)
        return redirect(permission_url)

    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest(e)


@track_statistics
def auth_callback(request):
    """
    After the user has approved our app, they are redirected from Shopify to us with a temporary code.
    We use this temporary code in exchange for a permanent one with offline access and store it in our db.
    """
    try:
        session = authenticate(request)
        params = parse_params(request)

        if not params['shop'].endswith('myshopify.com') or not re.match('^([A-Za-z0-9\-.]+)$', params['shop']):
            e = '{} is not a valid shopname'.format(params['shop'])
            logger.error(e)
            return HttpResponseBadRequest(e)

        token = session.request_token(params)

        request.session['shopify'] = {
            "params": params,
        }

        # Store permanent token or update if exists in db
        store, created = Store.objects.update_or_create(store_name=params['shop'],
                                                        defaults={'permanent_token': token, 'active': True,
                                                                  'shopify_api_scope': ','.join(
                                                                      settings.SHOPIFY_API_SCOPE)})

        return redirect('https://' + params['shop'] + '/admin/apps')
    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest(e)


@track_statistics
@xframe_options_exempt
def index(request):
    """
    This view is the entry point for our app in the store owner admin page.
    Redirects store owner to correct view based on account status.
    """

    try:
        session = authenticate(request)
        params = parse_params(request)

        params['app_url'] = settings.APP_URL
        params['api_key'] = settings.API_KEY

        request.session['shopify'] = {
            "params": params,
        }

        store_name = params['shop']

        exists_in_store_settings_table = StoreSettings.objects.filter(store__store_name=store_name).exists()
        exists_in_store_table = Store.objects.filter(store_name=store_name).exists()

        if not exists_in_store_table and not exists_in_store_settings_table:
            return HttpResponseRedirect(reverse('install'))

        if not exists_in_store_settings_table:
            # Populate database with default settings
            stores_obj = Store.objects.get(store_name=store_name)
            StoreSettings.objects.create(store=stores_obj)
            Modal.objects.create(store=stores_obj)

            ingest_products(stores_obj)
            ingest_orders(stores_obj)
            create_webhook(stores_obj)
            add_script(stores_obj, 'initializeModal.js')

        return HttpResponseRedirect(reverse('store_settings'))

    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest(e)


@track_statistics
@xframe_options_exempt
@shop_login_required
def store_settings(request):
    """
    App settings.
    """
    template = loader.get_template('app/index.html')
    params = request.session['shopify']['params']
    return HttpResponse(template.render(params, request))


@track_statistics
@xframe_options_exempt
@shop_login_required
@api_authentication
def store_settings_api(request, store_name):
    """
    Retrieve, update or delete store settings.
    """

    if request.method == 'GET':
        try:
            modal_obj = Modal.objects.filter(store__store_name=store_name).first()
            store_obj = Store.objects.filter(store_name=store_name).first()
            store_settings_obj = StoreSettings.objects.filter(store__store_name=store_name).first()

            response_dict = dict()
            response_dict['store_name'] = store_name
            response_dict['look_back'] = store_settings_obj.look_back

            response_dict['active'] = store_obj.active

            response_dict['social_setting'] = modal_obj.social_setting
            response_dict['color_brightness'] = modal_obj.color_brightness
            response_dict['color_hue'] = modal_obj.color_hue
            response_dict['color_saturation'] = modal_obj.color_saturation
            response_dict['size'] = modal_obj.size
            response_dict['location'] = modal_obj.location
            response_dict['social_scope'] = modal_obj.social_scope

            return JsonResponse(response_dict, safe=False)

        except Exception as e:
            logger.error(e)
            return HttpResponseBadRequest(e)

    elif request.method == 'POST':
        post_params = dict(request.POST.lists())

        try:
            store_settings_obj = StoreSettings.objects.get(store__store_name=store_name)
            modal_obj = Modal.objects.get(store__store_name=store_name)
        except Exception:
            return HttpResponseBadRequest('{} does not exist'.format(store_name), status=400)

        for key, value in post_params.items():
            if key == 'social_scope' and value[0] not in settings.SOCIAL_SCOPES:
                return HttpResponseBadRequest('{} is not a valid social scope'.format(value), status=400)

            if hasattr(store_settings_obj, key):
                setattr(store_settings_obj, key, value[0])
                store_settings_obj.save()
            if hasattr(modal_obj, key):
                setattr(modal_obj, key, value[0])
                modal_obj.save()

        return HttpResponse('Success', status=200)

    return HttpResponseBadRequest(status=400)


@track_statistics
@xframe_options_exempt
@shop_login_required
@api_authentication
def orders_api(request, store_name):
    """
    Return all orders for a given store name, e.g. mystore.myshopify.com.
    """
    if request.method == 'GET':
        qs1 = Orders.objects.filter(store__store_name=store_name)
        qs_json = serializers.serialize('json', qs1)
        return HttpResponse(qs_json, content_type='application/json')

    return HttpResponseBadRequest('Invalid request')


@track_statistics
@xframe_options_exempt
@shop_login_required
@api_authentication
def products_api(request, store_name):
    """
    Return all orders for a given store name, e.g. mystore.myshopify.com.
    """
    if request.method == 'GET':
        qs1 = Product.objects.filter(store__store_name=store_name)
        qs_json = serializers.serialize('json', qs1)
        return HttpResponse(qs_json, content_type='application/json')

    return HttpResponseBadRequest('Invalid request')


@track_statistics
def modal_api(request, store_name, product_id):
    """
    Public modal api. Returns a json string with relevant modal information.
    """
    if request.method == 'GET':
        try:
            # Returned products should be within store's look_back parameter
            look_back_qs = StoreSettings.objects.filter(store__store_name=store_name)

            if not look_back_qs:
                logger.error('{} does not exist'.format(store_name))
                return HttpResponseBadRequest('{} does not exist'.format(store_name), status=400)

            look_back = look_back_qs.values('look_back')[0]['look_back']
            time_threshold = timezone.now() - timedelta(seconds=look_back * 60 * 60)

            product_id_social = choice(find_products_from_social_scope(store_name, product_id))
            product_obj = Product.objects.filter(product_id=product_id_social).first()

            order_obj = Orders.objects \
                .filter(store__store_name=store_name) \
                .filter(product__product_id=product_id_social) \
                .filter(processed_at__range=[time_threshold, timezone.now()])
            order_obj_first = order_obj.first()
            modal_obj = Modal.objects.filter(store__store_name=store_name).first()

            collection_obj = Collection.objects.filter(product__product_id=product_id_social).values('collection_id')
            collection_ids = ','.join([k['collection_id'] for k in list(collection_obj)])

            response_dict = dict()
            response_dict['store_name'] = store_name
            response_dict['product_id'] = product_id_social
            response_dict['look_back'] = look_back

            response_dict['main_image_url'] = product_obj.main_image_url if hasattr(product_obj,
                                                                                    'main_image_url') and product_obj.main_image_url != '' else None
            response_dict['handle'] = product_obj.handle if hasattr(product_obj, 'handle') else None
            response_dict['product_type'] = product_obj.product_type if hasattr(product_obj, 'product_type') else None
            response_dict['vendor'] = product_obj.vendor if hasattr(product_obj, 'vendor') else None
            response_dict['tags'] = product_obj.tags if hasattr(product_obj, 'tags') else None
            response_dict['product_name'] = product_obj.product_name if hasattr(product_obj, 'product_name') else None

            response_dict['collection_ids'] = collection_ids if collection_ids else None

            response_dict['social_setting'] = modal_obj.social_setting
            response_dict['color_brightness'] = modal_obj.color_brightness
            response_dict['color_hue'] = modal_obj.color_hue
            response_dict['color_saturation'] = modal_obj.color_saturation
            response_dict['size'] = modal_obj.size
            response_dict['location'] = modal_obj.location
            response_dict['social_scope'] = modal_obj.social_scope

            response_dict['first_name'] = order_obj_first.first_name if hasattr(order_obj_first, 'first_name') else None
            response_dict['last_name'] = order_obj_first.last_name if hasattr(order_obj_first, 'last_name') else None
            response_dict['province_code'] = order_obj_first.province_code if hasattr(order_obj_first,
                                                                                      'province_code') else None
            response_dict['country_code'] = order_obj_first.country_code if hasattr(order_obj_first,
                                                                                    'country_code') else None
            response_dict['last_order_qty'] = order_obj_first.qty if hasattr(order_obj_first, 'qty') else None
            response_dict['processed_at'] = order_obj_first.processed_at if hasattr(order_obj_first,
                                                                                    'processed_at') else None
            response_dict['qty_from_look_back'] = order_obj.aggregate(Sum('qty'))['qty__sum']

            return JsonResponse(response_dict, safe=False)
        except Exception as e:
            logger.error(e)
            return HttpResponseBadRequest('Something went wrong.')

    return HttpResponseBadRequest('Invalid request')


@track_statistics
def related_products_api(request, store_name, product_id):
    """
    Public related products api. Returns a json string with list of related products based store's social scope.
    """
    if request.method == 'GET':
        try:
            response_dict = dict()
            related_product_ids = find_products_from_social_scope(store_name, product_id)
            response_dict['related_product_ids'] = ','.join(related_product_ids)
            return JsonResponse(response_dict, safe=False)
        except Exception as e:
            logger.error(e)
            return HttpResponseBadRequest('Something went wrong.')

    return HttpResponseBadRequest('Invalid request')


@track_statistics
def modal_metrics_api(request):
    """
    Public modal metrics api. Stores metrics click data to our database.
    """

    if request.method == 'POST':
        try:
            post_params = dict(request.POST.lists())
            snapshot_date = date.today()
            store_name = post_params['store_name'][0]
            product_id_from = post_params['product_id_from'][0]
            product_id_to = post_params['product_id_to'][0]

            try:
                product_id_from_obj = Product.objects.get(product_id=product_id_from, store__store_name=store_name)
                product_id_to_obj = Product.objects.get(product_id=product_id_to, store__store_name=store_name)
                store_obj = Store.objects.get(store_name=store_name)
            except (Store.DoesNotExist, Product.DoesNotExist):
                logger.error(
                    'Product {} or {} or Store {} does not exist'.format(product_id_from, product_id_to, store_name))
                return HttpResponseBadRequest(
                    'Product {} or {} or Store {} does not exist'.format(product_id_from, product_id_to, store_name))

            try:
                api_metrics_obj = ModalMetrics.objects.get(snapshot_date=snapshot_date, product_id_to=product_id_to_obj,
                                                           product_id_from=product_id_from_obj, store=store_obj)
                api_metrics_obj.click_count += 1
                api_metrics_obj.save()
            except Exception as e:
                ModalMetrics.objects.create(snapshot_date=snapshot_date, product_id_to=product_id_to_obj,
                                            product_id_from=product_id_from_obj, store=store_obj, click_count=1)

            return HttpResponse('Success', status=200)
        except Exception:
            return HttpResponseBadRequest('Invalid post parameters provided', status=400)

    return HttpResponseBadRequest('Invalid request')


@track_statistics
def webhooks(request):
    """
    Webhook for uninstalling app.
    """
    if request.method == 'POST':
        try:
            store_name = request.META.get('HTTP_X_SHOPIFY_SHOP_DOMAIN')
            Store.objects.filter(store_name=store_name).delete()
            return HttpResponse('Success', status=200)
        except Exception as e:
            logger.error('Something bad happened with uninstall {}'.format(e))
            return HttpResponseBadRequest('Something bad happened with uninstall {}'.format(e))

    return HttpResponseBadRequest('Invalid request')
