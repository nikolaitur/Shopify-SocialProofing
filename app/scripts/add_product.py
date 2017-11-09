# Development test script to generate a dummy product. Run using Pyton 2.7.x.
# More information here: https://help.shopify.com/api/reference

import shopify
import random
import ssl

# Overrides the default function for context creation with the function to create an unverified context.
ssl._create_default_https_context = ssl._create_unverified_context

# Authentication
token = '11461aafd388df61fa87b44dfe1fe430'
session = shopify.Session("michael-john-devs.myshopify.com.myshopify.com", token)
shopify.ShopifyResource.activate_session(session)

# Add a new product
new_product = shopify.Product()
new_product.title = "Burton Custom Freestyle %s" % random.randint(0, 9999)
new_product.product_type = "Snowboard"
new_product.vendor = "Burton"
success = new_product.save()
