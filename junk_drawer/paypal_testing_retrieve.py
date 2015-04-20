import paypalrestsdk
import os

PAYPAL_CLIENT_ID=os.environ['PAYPAL_CLIENT_ID']
PAYPAL_CLIENT_SECRET=os.environ['PAYPAL_CLIENT_SECRET']

paypalrestsdk.configure({
    "mode": "sandbox", # sandbox or live
    "client_id": PAYPAL_CLIENT_ID,
    "client_secret": PAYPAL_CLIENT_SECRET })

payment=paypalrestsdk.Payment.find('PAY-5TR59111W02844217KUZM23Y')

payment_dict=payment.to_dict()




