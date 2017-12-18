# Development test script to add script tag to store.
# More information here: https://help.shopify.com/api/reference

import shopify
import ssl
import sys
import os
import django
import logging

sys.path.append("..")  # here store is root folder(means parent).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from app.models import Store
from django.conf import settings
from slacker_log_handler import SlackerLogHandler

# Overrides the default function for context creation with the function to create an unverified context.
ssl._create_default_https_context = ssl._create_unverified_context

slack_handler = SlackerLogHandler(settings.SLACK_API_KEY, 'production-logs', stack_trace=True)

logger = logging.getLogger(__name__)
logger.addHandler(slack_handler)


def authenticate(func):
    def wrapper(stores_obj, *args, **kwargs):
        session = shopify.Session(stores_obj.store_name, stores_obj.permanent_token)
        shopify.ShopifyResource.activate_session(session)
        return func(stores_obj, *args, **kwargs)

    return wrapper


@authenticate
def add_script(stores_obj, script_name):
    # Development app url: https://protected-reef-37693.herokuapp.com
    # Production app url: https://socialproof-samurai.herokuapp.com

    # Add script tag to the shop
    src = '{}/static/js/{}'.format(settings.APP_URL, script_name)

    try:
        shopify.ScriptTag(dict(display_scope='all', event='onload', src=src)).save()
    except Exception as e:
        logger.error('Exception caught for {}. {}'.format(stores_obj.store_name, e))


@authenticate
def delete_all_scripts(stores_obj):
    try:
        [shopify.ScriptTag.delete(x.id) for x in shopify.ScriptTag.find()]
    except Exception as e:
        logger.error('Exception caught for {}. {}'.format(stores_obj.store_name, e))


@authenticate
def delete_script_by_id(stores_obj, script_tag_id):
    try:
        script_tag_obj = (shopify.ScriptTag().find(script_tag_id))
        shopify.ScriptTag.delete(script_tag_obj.id)
    except Exception as e:
        logger.error('Exception caught for {}. {}'.format(stores_obj.store_name, e))


@authenticate
def print_script_info(stores_obj):
    try:
        # Print how many script tags added already
        print(shopify.ScriptTag().count())

        # Loop through each script tag and print attributes of each
        for script_tag in shopify.ScriptTag().find():
            print(script_tag.attributes)
    except Exception as e:
        logger.error('Exception caught for {}. {}'.format(stores_obj.store_name, e))


if __name__ == '__main__':
    store_name = 'michaeljohnsecond.myshopify.com'
    stores_obj = Store.objects.get(store_name=store_name)

    print_script_info(stores_obj)

    script_name = 'initializeModal.js'
    add_script(stores_obj, script_name)

    # delete_all_scripts(stores_obj)
