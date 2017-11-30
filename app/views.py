import logging
from urllib.parse import urlparse

import shopify
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.template import loader
from django.views.decorators.clickjacking import xframe_options_exempt
from django.db.models import Sum

from .utils import authenticate, parse_params, populate_default_settings
from .decorators import shop_login_required, api_authentication, track_statistics
from .models import Store, StoreSettings, Modal, Orders, Product, Collection, ModalMetrics
from django.core import serializers
from datetime import date
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


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
        token = session.request_token(params)
        logger.info('Received permanent token: {} from {}'.format(token, params['shop']))

        request.session['shopify'] = {
            "shop_url": params['shop']
        }

        # Store permanent token or update if exists in db
        store, created = Store.objects.update_or_create(store_name=params['shop'],
                                                        defaults={'permanent_token': token, 'active': True})

        # Return the user back to their shop
        return redirect('https://' + params['shop'])
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

        request.session['shopify'] = {
            "shop_url": params['shop']
        }

        store_name = params['shop']

        exists_in_store_settings_table = StoreSettings.objects.filter(store__store_name=store_name).exists()
        exists_in_store_table = Store.objects.filter(store_name=store_name).exists()

        if not exists_in_store_table and not exists_in_store_settings_table:
            return HttpResponseRedirect(reverse('install'))

        if exists_in_store_table and not exists_in_store_settings_table:
            populate_default_settings(store_name)  # Populate store settings with defaults in db

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
    params = parse_params(request)
    return HttpResponse(template.render())


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

            order_obj = Orders.objects \
                .filter(store__store_name=store_name) \
                .filter(product__product_id=product_id) \
                .filter(processed_at__range=[time_threshold, timezone.now()])
            order_obj_first = order_obj.first()
            modal_obj = Modal.objects.filter(store__store_name=store_name).first()
            product_obj = Product.objects.filter(product_id=product_id).first()

            collection_obj = Collection.objects.filter(product__product_id=product_id).values('collection_id')
            collection_ids = ', '.join([k['collection_id'] for k in list(collection_obj)])

            response_dict = dict()
            response_dict['store_name'] = store_name
            response_dict['product_id'] = product_id

            response_dict['main_image_url'] = product_obj.main_image_url if hasattr(product_obj,
                                                                                    'main_image_url') and product_obj.main_image_url != '' else None
            response_dict['handle'] = product_obj.handle if hasattr(product_obj, 'handle') else None
            response_dict['product_type'] = product_obj.product_type if hasattr(product_obj, 'product_type') else None
            response_dict['vendor'] = product_obj.vendor if hasattr(product_obj, 'vendor') else None
            response_dict['tags'] = product_obj.tags if hasattr(product_obj, 'tags') else None

            response_dict['collection_ids'] = collection_ids if collection_ids else None

            response_dict['social_setting'] = modal_obj.social_setting
            response_dict['color_brightness'] = modal_obj.color_brightness
            response_dict['color_hue'] = modal_obj.color_hue
            response_dict['color_saturation'] = modal_obj.color_saturation
            response_dict['size'] = modal_obj.size
            response_dict['location'] = modal_obj.location

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
def related_products_api(request, store_name, product_id, search_type):
    """
    Public related products api. Returns a json string with list of related products based on search type.
    """
    if request.method == 'GET':
        try:
            related_product_ids = set()
            response_dict = dict()

            products = Product.objects.filter(store__store_name=store_name).values()
            collections = Collection.objects.filter(product__store__store_name=store_name)

            target_product = Product.objects.filter(store__store_name=store_name, product_id=product_id).first()
            target_collection = Collection.objects.filter(product__product_id=product_id).first()

            response_dict['store_name'] = store_name
            response_dict['product_id'] = product_id
            response_dict['search_type'] = search_type
            response_dict['related_product_ids'] = ''

            if not target_product or not target_collection:
                return JsonResponse(response_dict, safe=False)

            for product in products:
                if product['product_id'] == target_product.product_id:
                    continue

                if 'vendor' in search_type and product['vendor'] == target_product.vendor:
                    related_product_ids.add(product['product_id'])
                    continue

                if 'product_type' in search_type and product['product_type'] == target_product.product_type:
                    related_product_ids.add(product['product_id'])
                    continue

                # Any word in target tag matches in product tag
                if 'tags' in search_type and len(
                                set(target_product.tags.split(', ')) & set(product['tags'].split(', '))) > 0:
                    related_product_ids.add(product['product_id'])
                    continue

            for collection in collections:
                if collection.get_product_id() == target_product.product_id:
                    continue

                if 'collection' in search_type and target_collection.collection_id == collection.collection_id:
                    related_product_ids.add(collection.get_product_id())
                    continue

            related_product_ids = list(related_product_ids)
            response_dict['related_product_ids'] = ', '.join(related_product_ids)

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
