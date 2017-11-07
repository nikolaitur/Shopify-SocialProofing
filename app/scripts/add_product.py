# Development test script to generate a dummy product. Run using Pyton 2.7.x.
# More information here: https://help.shopify.com/api/reference

import shopify
import random

# Authentication
token = 'e8c49b1c40bde5e8bf956703f5f62797'
session = shopify.Session("michael-john-devs.myshopify.com.myshopify.com", token)
shopify.ShopifyResource.activate_session(session)

# Add a new product
new_product = shopify.Product()
new_product.title = "Burton Custom Freestyle %s" % random.randint(0,9999)
new_product.product_type = "Snowboard"
new_product.vendor = "Burton"
success = new_product.save()