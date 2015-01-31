import paypalrestsdk
import os, ast
from aux import *

PRODUCTION_STATUS='test'

PAYPAL_CLIENT_ID=get_env_var('paypal',PRODUCTION_STATUS,'PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET=get_env_var('paypal',PRODUCTION_STATUS,'PAYPAL_CLIENT_SECRET')


paypalrestsdk.configure({
    "mode": "sandbox", # sandbox or live
    "client_id": PAYPAL_CLIENT_ID,
    "client_secret": PAYPAL_CLIENT_SECRET })


invoice_number=id_generator()

items_LOD=[dict(
    quantity="1",
    name="eCig Drip Tip",
    price="20.00",
    currency="USD",
    description="Description of item",
    ),
           dict(
    quantity="1",
    name="eCig Drip Tip Black",
    price="20.00",
    currency="USD",
    description="Description of item",
    ),
]

## Initiate a payment
payment_dict=paypal_create_payment_dict(
    intent='sale',
    payment_method='paypal', 
    redirect_urls=dict(
        return_url="https://threemusesglass.herokuapp.com/paypal_webhooks",
        cancel_url="https://threemusesglass.herokuapp.com"),
    cost_dict=dict(
        shipping_cost_USD=2.00, 
        cart_cost_USD=40, 
        total_cost_USD=42),
    transaction_description='Purchase from ThreeMusesGlass',
    invoice_number=invoice_number,
    items_paypal_list_of_dicts=items_LOD,)

payment=paypalrestsdk.Payment(payment_dict)

payment_boolean=payment.create()

## send user to paypal to confirm payment

approval_url=payment['links'][1]['href']

print approval_url



#https://threemusesglass.herokuapp.com/?paymentId=PAY-6LV41146RP9752910KTB7GTY&token=EC-9F778084G1126725T&PayerID=DANUSGV96JSPL


## execute payment

#sale_boolean=payment.execute({"payer_id":"DANUSGV96JSPL"})

##    status=""
##    if payment.create():
##        status="Created successfully"
##        session.paypal_response=payment
##    else:
##        status=payment.error
