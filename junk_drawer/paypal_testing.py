import paypalrestsdk
import os, ast

try:
    ## see if you can acces the heroku environment variables
    PAYPAL_CLIENT_ID=os.environ['PAYPAL_CLIENT_ID']
    PAYPAL_CLIENT_SECRET=os.environ['PAYPAL_CLIENT_SECRET']

## what exception exactly?
except KeyError:

    # you aren't running on heroku
    # this will fail if it can't find the local keys. GOOD.
    with open('/home/wantsomechocolate/Code/API Info/api_keys.txt','r') as fh:
        text=fh.read()
        api_keys = ast.literal_eval(text)
    
    PAYPAL_CLIENT_ID=api_keys['paypal']['test']['PAYPAL_CLIENT_ID']
    PAYPAL_CLIENT_SECRET=api_keys['paypal']['test']['PAYPAL_CLIENT_SECRET']


paypalrestsdk.configure({
    "mode": "sandbox", # sandbox or live
    "client_id": PAYPAL_CLIENT_ID,
    "client_secret": PAYPAL_CLIENT_SECRET })

payment=paypalrestsdk.Payment({

    "intent": "sale",

    "payer": {
        "payment_method": "paypal",
        #"payer_info":{} Prefilled when payment method is paypal
        },

    "transactions": [

            {
                "amount":{
                    "currency":"USD",
                    "total":"100.25",
                },

                "description":"Test transaction description",

                "invoice_number":"A3H2JK89SZ",

            },

        ],

    "redirect_urls":{
        "return_url":"https://threemusesglass.herokuapp.com",
        "cancel_url":"https://threemusesglass.herokuapp.com/categories",
        }
    })

payment.create()

##    status=""
##    if payment.create():
##        status="Created successfully"
##        session.paypal_response=payment
##    else:
##        status=payment.error
