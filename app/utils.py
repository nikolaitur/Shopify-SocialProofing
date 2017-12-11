import shopify
import logging

from django.conf import settings
from .models import StoreSettings, Store, Modal, Product, Collection

logger = logging.getLogger(__name__)


def authenticate(request):
    """
    Authenticates user requests to the app.

    :param request: Django Request Object
    :return:        Shopify session with shop name.
    """
    shopify.Session.setup(api_key=settings.API_KEY, secret=settings.API_SECRET)

    try:
        params = parse_params(request)
        session = shopify.Session(params['shop'])
        if settings.DEVELOPMENT_MODE == 'PRODUCTION':
            if not session.validate_params(params=params):
                raise Exception('Invalid HMAC: Possibly malicious login')

        return session
    except Exception as e:
        logger.error(e)
        raise Exception('Failed to authenticate request')


def parse_params(request):
    """
    Parse authentication GET parameters.
    """
    try:
        if request.method == 'GET':
            params = {}

            if 'code' in request.GET:
                params['code'] = request.GET['code']
            if 'hmac' in request.GET:
                params['hmac'] = request.GET['hmac']
            if 'locale' in request.GET:
                params['locale'] = request.GET['locale']
            if 'protocol' in request.GET:
                params['protocol'] = request.GET['protocol']
            if 'shop' in request.GET:
                params['shop'] = request.GET['shop']
            if 'timestamp' in request.GET:
                params['timestamp'] = request.GET['timestamp']

        return params
    except Exception as e:
        logger.error(e)
        raise Exception('Failed to parse URI parameters')


def populate_default_settings(store_name):
    """
    Populate db with default settings
    """

    try:
        store = Store.objects.get(store_name=store_name)
    except Store.DoesNotExist:
        store = store.objects.create(store_name=store_name)

    StoreSettings.objects.create(store=store)
    Modal.objects.create(store=store)


def find_products_from_social_scope(store_name, product_id):
    """
    Returns a list of products ids based on a store's social scope.
    """

    try:
        related_product_ids = set()

        modal_obj = Modal.objects.filter(store__store_name=store_name).first()
        social_scope = modal_obj.social_scope

        if social_scope == 'product':
            return [product_id]

        products = Product.objects.filter(store__store_name=store_name).values()

        if social_scope == 'any':
            return [x['product_id'] for x in products.values('product_id')]

        collections = Collection.objects.filter(product__store__store_name=store_name)
        target_product = Product.objects.filter(store__store_name=store_name, product_id=product_id).first()
        target_collection = Collection.objects.filter(product__product_id=product_id).first()

        if target_product:
            for product in products:
                if product['product_id'] == target_product.product_id:
                    continue

                if 'vendor' == social_scope and product['vendor'] == target_product.vendor:
                    related_product_ids.add(product['product_id'])
                    continue

                if 'product_type' == social_scope and product['product_type'] == target_product.product_type:
                    related_product_ids.add(product['product_id'])
                    continue

                # Any word in target tag matches in product tag
                if 'tags' == social_scope and len(
                                set(target_product.tags.split(', ')) & set(product['tags'].split(', '))) > 0:
                    related_product_ids.add(product['product_id'])
                    continue

        if target_collection:
            for collection in collections:
                if collection.get_product_id() == target_product.product_id:
                    continue

                if 'collections' in social_scope and target_collection.collection_id == collection.collection_id:
                    related_product_ids.add(collection.get_product_id())
                    continue

        related_product_ids = list(related_product_ids)

        # Return same product id if no matching products found within scope
        if len(related_product_ids) == 0:
            return [product_id]

        return related_product_ids
    except Exception as e:
        logger.error(e)
        return []
