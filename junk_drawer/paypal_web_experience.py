import paypalrestsdk
from paypalrestsdk import WebProfile, Payment
import os, ast
from aux import *

PRODUCTION_STATUS='test'

PAYPAL_CLIENT_ID=get_env_var('paypal',PRODUCTION_STATUS,'PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET=get_env_var('paypal',PRODUCTION_STATUS,'PAYPAL_CLIENT_SECRET')


paypalrestsdk.configure({
    "mode": "sandbox", # sandbox or live
    "client_id": PAYPAL_CLIENT_ID,
    "client_secret": PAYPAL_CLIENT_SECRET })


web_profile = WebProfile({
    "name": "ThreeMusesGlass01",
    "presentation": {
        "brand_name": "YeowZa Paypal",
        "logo_image": "http://s3-ec.buzzfed.com/static/2014-07/18/8/enhanced/webdr02/anigif_enhanced-buzz-21087-1405685585-12.gif",
        "locale_code": "US"
    },
    "input_fields": {
        "allow_note": True,
        "no_shipping": 1,
        "address_override": 1
    },
    "flow_config": {
        "landing_page_type": "billing",
        "bank_txn_pending_url": "http://www.yeowza.com"
    }
})


if web_profile.create():
    print("Web Profile[%s] created successfully" % (web_profile.id))
else:
    print(web_profile.error)
