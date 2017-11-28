import shopify
import ssl
import sys
import os
import django

sys.path.append("..")  # here store is root folder(means parent).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from app.models import Store, Product, Orders
from dateutil.parser import parse

# Overrides the default function for context creation with the function to create an unverified context.
ssl._create_default_https_context = ssl._create_unverified_context


def get_stores():
    """
    Return all store names and permanent tokens as dictionary.
    """
    return Store.objects.all().values('store_name', 'permanent_token', 'active')


def ingest_orders(stores_obj):
    """
    Query each store in database and save orders to Orders table.
    """

    session = shopify.Session(stores_obj['store_name'], stores_obj['permanent_token'])
    shopify.ShopifyResource.activate_session(session)
    store = Store.objects.get(store_name=stores_obj['store_name'])
    orders = shopify.Order.find()

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
            Orders.objects.update_or_create(order_id=order_id, store__store_name=stores_obj['store_name'],
                                            product=product,
                                            defaults={'product': product,
                                                      'store': store,
                                                      'qty': qty,
                                                      'processed_at': processed_at,
                                                      'first_name': first_name,
                                                      'last_name': last_name,
                                                      'province_code': province_code,
                                                      'country_code': country_code, })


def ingest_products(stores_obj):
    """
    Query each store in database and save products to Product table.
    """
    session = shopify.Session(stores_obj['store_name'], stores_obj['permanent_token'])
    shopify.ShopifyResource.activate_session(session)
    store = Store.objects.get(store_name=stores_obj['store_name'])
    product_listings = shopify.Product.find()

    for product_listing in product_listings:
        product_id = product_listing.id
        product_name = product_listing.title
        product_images = product_listing.images

        main_image_url = ''
        if product_images:
            position = product_images[0].attributes['position']
            assert position == 1, 'Warning: Image may not be the main image (not position 1).'
            main_image_url = product_images[0].attributes['src']

        Product.objects.update_or_create(product_id=product_id, store__store_name=stores_obj['store_name'],
                                         defaults={'product_name': product_name, 'store': store,
                                                   'main_image_url': main_image_url})


if __name__ == '__main__':
    stores_objs = get_stores()
    for stores_obj in stores_objs:
        if stores_obj['active']:
            ingest_products(stores_obj)
            ingest_orders(stores_obj)
