import shopify
import ssl
import sys
import os
import datetime
import django
import logging

sys.path.append("..")  # here store is root folder(means parent).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from app.models import Store, Product, Orders, Collection
from dateutil.parser import parse
from django.conf import settings
from slacker_log_handler import SlackerLogHandler

# Overrides the default function for context creation with the function to create an unverified context.
ssl._create_default_https_context = ssl._create_unverified_context

slack_handler = SlackerLogHandler(settings.SLACK_API_KEY, 'production-logs', stack_trace=True)

logger = logging.getLogger(__name__)

if settings.DEVELOPMENT_MODE == 'PRODUCTION':
    logger.addHandler(slack_handler)


def get_stores():
    """
    Return all store names and permanent tokens as dictionary.
    """
    return Store.objects.all()


def ingest_orders(stores_obj):
    """
    Query each store in database and save orders to Orders table.
    """
    try:
        session = shopify.Session(stores_obj.store_name, stores_obj.permanent_token)
        shopify.ShopifyResource.activate_session(session)
        store = Store.objects.get(store_name=stores_obj.store_name)
        created_at_min = datetime.datetime.now() - datetime.timedelta(days=10)
        orders = shopify.Order.find(financial_status='paid', status='shipped', created_at_min=created_at_min)

        for order in orders:
            customer = order.attributes.get('customer', None)
            shipping_address = order.attributes.get('shipping_address', None)

            first_name = ''
            last_name = ''
            province_code = ''
            country_code = ''

            if customer:
                first_name = customer.attributes['first_name']
                last_name = customer.attributes['last_name'][0] + '.'  # First letter of last name

            if shipping_address:
                province_code = shipping_address.attributes['province_code']
                country_code = shipping_address.attributes['country_code']

            order_id = order.id
            processed_at = parse(order.processed_at)

            for line_item in order.line_items:
                qty = line_item.quantity
                product_id = line_item.product_id

                if product_id is None:
                    continue

                product = Product.objects.get(product_id=product_id)
                Orders.objects.update_or_create(order_id=order_id, store__store_name=stores_obj.store_name,
                                                product=product,
                                                defaults={'product': product,
                                                          'store': store,
                                                          'qty': qty,
                                                          'processed_at': processed_at,
                                                          'first_name': first_name,
                                                          'last_name': last_name,
                                                          'province_code': province_code,
                                                          'country_code': country_code, })
    except Exception as e:
        logger.error('Exception caught for {}. {}'.format(stores_obj.store_name, e))


def ingest_products(stores_obj):
    """
    Query each store in database and save products to Product table.
    """
    try:
        session = shopify.Session(stores_obj.store_name, stores_obj.permanent_token)
        shopify.ShopifyResource.activate_session(session)
        store = Store.objects.get(store_name=stores_obj.store_name)
        product_listings = shopify.Product.find()
        collection_listings = shopify.Collect.find()

        for product_listing in product_listings:
            product_id = product_listing.id
            product_name = product_listing.title
            product_image = product_listing.image
            handle = product_listing.handle
            tags = product_listing.tags

            vendor = product_listing.vendor if product_listing.vendor else ''
            product_type = product_listing.product_type if product_listing.product_type else ''
            main_image_url = product_image.attributes['src'] if product_image else ''

            Product.objects.update_or_create(product_id=product_id, store__store_name=stores_obj.store_name,
                                             defaults={'product_name': product_name, 'store': store,
                                                       'main_image_url': main_image_url,
                                                       'handle': handle,
                                                       'vendor': vendor,
                                                       'tags': tags,
                                                       'product_type': product_type})

        for collection_listing in collection_listings:
            collection_id = collection_listing.attributes['collection_id']
            product_id = collection_listing.attributes['product_id']

            product = Product.objects.get(product_id=product_id)
            Collection.objects.update_or_create(product=product, collection_id=collection_id,
                                                defaults={'collection_id': collection_id})

    except Exception as e:
        logger.error('Exception caught for {}. {}'.format(stores_obj.store_name, e))


if __name__ == '__main__':
    stores_objs = get_stores()
    for stores_obj in stores_objs:
        if stores_obj.active:
            ingest_products(stores_obj)
            ingest_orders(stores_obj)
    print('Success.')
