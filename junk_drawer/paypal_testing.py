import paypalrestsdk
import os, ast

## Get your paypal keys
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



## Get an Access token






## Initiate a payment
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

payment_boolean=payment.create()


## send user to paypal to confirm payment

approval_url=payment['links'][1]['href']
print approval_url



#https://threemusesglass.herokuapp.com/?paymentId=PAY-6LV41146RP9752910KTB7GTY&token=EC-9F778084G1126725T&PayerID=DANUSGV96JSPL


## execute payment

sale_boolean=payment.execute({"payer_id":"DANUSGV96JSPL"})

##    status=""
##    if payment.create():
##        status="Created successfully"
##        session.paypal_response=payment
##    else:
##        status=payment.error
