import string
import random

def get_env_var(service, test_or_live, key):
    import os
    return os.environ[key]



def id_generator(size=16, chars=string.ascii_uppercase + string.digits):

    return ''.join(random.choice(chars) for _ in range(size))


def paypal_create_payment_dict(
        intent='sale', 
        payment_method='paypal', 
        experience_profile_id=None,
        redirect_urls=dict(return_url=None,cancel_url=None),
        cost_dict=dict(shipping_cost_USD=None, cart_cost_USD=None, total_cost_USD=None),
        transaction_description='Purchase from ThreeMusesGlass',
        invoice_number=id_generator(),
        items_paypal_list_of_dicts=None,
    ):

    ## Initialize payment_dict
    payment_dict={}

    ## Prepare and ad the intent
    payment_dict['intent']=intent


    ## Add experience ID!
    payment_dict['experience_profile_id']=experience_profile_id#"XP-NCB5-MNX5-G4SA-CDTH"


    ## Prepare and add the payer_dict
    payer_dict={}
    payer_dict['payment_method']=payment_method
    payment_dict['payer']=payer_dict




    ## Testing to see if I can tell paypal the shipping address on a per order basis

    ## Create the shipping_address_dict
    shipping_address_dict=dict(
        recipient_name="James",
        type="residential",
        line1="363 Cranbury Rd",
        line2="Apt D9",
        city="East Brunswick",
        country_code="US",
        postal_code="08816",
        state="NJ",
        )

    ## Creat the payer_info_dict
    payer_info_dict={}

    ## Add the shipping_address_dict to the payer_info_dict
    payer_info_dict['shipping_address']=shipping_address_dict

    ## Add the payer_info_dict to the payer_dict
    payer_dict['payer_info']=payer_info_dict




    ## Prepare and add the redirect URLs
    redirect_urls_dict={}
    redirect_urls_dict['return_url']=redirect_urls['return_url']
    redirect_urls_dict['cancel_url']=redirect_urls['cancel_url']
    payment_dict['redirect_urls']=redirect_urls_dict


    ## Prepare and add the transactions
    transactions_dict={}

    amount_dict={}

    amount_dict['currency']='USD'
    amount_dict['total']='{:.2f}'.format(cost_dict['total_cost_USD'])

    details_dict={}
    details_dict['shipping']='{:.2f}'.format(cost_dict['shipping_cost_USD'])
    details_dict['subtotal']='{:.2f}'.format(cost_dict['cart_cost_USD'])

    amount_dict['details']=details_dict

    items_LOD=items_paypal_list_of_dicts

    item_list=dict(items=items_LOD)

    transactions_dict['amount']=amount_dict
    transactions_dict['description']=transaction_description
    transactions_dict['invoice_number']=invoice_number
    transactions_dict['item_list']=item_list

    transaction_LOD=[transactions_dict]

    payment_dict['transactions']=transaction_LOD

    return payment_dict



## The next two function are taken from here:
## http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-camel-case
## from the answer given by user jdavidls to solve CaptialCase -> Capital Case conversion. It works great!
## But I have no idea how or why. 

def splitSymbol(s):
    si, ci, state = 0, 0, 0 # start_index, current_index 
    '''
        state bits:
        0: no yields
        1: lower yields
        2: lower yields - 1
        4: upper yields
        8: digit yields
        16: other yields
        32 : upper sequence mark
    '''
    for c in s:

        if c.islower():
            if state & 1:
                yield s[si:ci]
                si = ci
            elif state & 2:
                yield s[si:ci - 1]
                si = ci - 1
            state = 4 | 8 | 16
            ci += 1

        elif c.isupper():
            if state & 4:
                yield s[si:ci]
                si = ci
            if state & 32:
                state = 2 | 8 | 16 | 32
            else:
                state = 8 | 16 | 32

            ci += 1

        elif c.isdigit():
            if state & 8:
                yield s[si:ci]
                si = ci
            state = 1 | 4 | 16
            ci += 1

        else:
            if state & 16:
                yield s[si:ci]
            state = 0
            ci += 1  # eat ci
            si = ci   
        #print(' : ', c, bin(state))
    if state:
        yield s[si:ci] 


def camelcaseToUnderscore(s):
    return ' '.join(splitSymbol(s))

def create_shipment(to_address_dict, shipping_cart_LOD):
    import easypost

    package_weight_oz=0
    for item in shipping_cart_LOD:
        package_weight_oz+=float(item['product_weight'])*float(item['product_qty'])

    from_address=easypost.Address.create(
        company='threemusesglass',
        street1='308 Clearcreek Rd',
        city='Myrtle Beach',
        state='SC',
        zip='29572',
    )

    parcel=easypost.Parcel.create(
        #price really depends on weight so the dimensions are hard coded in here for now
        length=8,
        width=8,
        height=4,
        weight=package_weight_oz,
    )

    # If the package is shipping domestic
    if to_address_dict['country']=='United States':

        to_address=easypost.Address.create(
            #name = to_address_dict['name'],
            street1=to_address_dict['street_address_line_1'], 
            street2=to_address_dict['street_address_line_2'],
            city = to_address_dict['municipality'],
            state = to_address_dict['administrative_area'],
            zip = to_address_dict['postal_code'],
        )

        shipment=easypost.Shipment.create(
            to_address = to_address,
            from_address = from_address,
            parcel=parcel,
        )

    else:

        to_address=easypost.Address.create(
            #name = to_address_dict['name'],
            street1=to_address_dict['street_address_line_1'], 
            street2=to_address_dict['street_address_line_2'],
            city = to_address_dict['municipality'],
            state = to_address_dict['administrative_area'],
            zip = to_address_dict['postal_code'],
            country=to_address_dict['country'],
        )

        customs_items=[]
        for item in shipping_cart_LOD:
            customs_item=easypost.CustomsItem.create(
                description=item['product_shipping_desc'],
                quantity=item['product_qty'],
                value=item['product_cost'],
                weight=float(item['product_weight']),
                ## This is most generic tariff number for glass
                hs_tariff_number=700100,
                origin_country='US',
            )
            customs_items.append(customs_item)

        if to_address_dict['country']=='Canada':

            customs_info=easypost.CustomsInfo.create(
                customs_items=customs_items,
                contents_type='merchandise',
                #contents_explanation=None,
                restriction_type='none',
                #restriction_comments=None,
                customs_certify=True,
                customs_signer='James McGlynn',
                non_delivery_option='return',
                eel_pfc='NOEEI 30.36',
            )

        else:

            customs_info=easypost.CustomsInfo.create(
                customs_items=customs_items,
                contents_type='merchandise',
                #contents_explanation=None,
                restriction_type='none',
                #restriction_comments=None,
                customs_certify=True,
                customs_signer='James McGlynn',
                non_delivery_option='return',
                eel_pfc='NOEEI 30.37(a).',
            )

        shipment=easypost.Shipment.create(
            to_address=to_address,
            from_address=from_address,
            parcel=parcel,
            customs_info=customs_info,
        )

    return shipment



def create_purchase_history_dict(

    session_data,
    user_data,
    address_data,
    payment_service,
    payment_data,
    summary_data,
    ):

    import json

    easypost_response=json.loads(address_data['easypost_api_response'])

    rates=easypost_response['rates']

    default_rate=address_data['easypost_default_shipping_rate_id']

    rate_info={}

    for rate in rates:
        if rate['id']==default_rate:
            rate_info=rate


    purchase_history_data_dict=dict(

        session_id_3muses=session_data.session_id_3muses,
        session_db_table=session_data.session_db_table,
        session_db_record_id=session_data.session_db_record_id,

        muses_id=user_data.id,
        muses_email_address=user_data.email,
        muses_name=user_data.first_name,

        shipping_street_address_line_1=address_data['street_address_line_1'],
        shipping_street_address_line_2=address_data['street_address_line_2'],
        shipping_municipality=address_data['municipality'],
        shipping_administrative_area=address_data['administrative_area'],
        shipping_postal_code=address_data['postal_code'],
        shipping_country=address_data['country'],

        easypost_shipping_service=rate_info['service'],
        easypost_shipping_carrier=rate_info['carrier'],
        easypost_shipment_id=rate_info['shipment_id'],
        easypost_rate_id=rate_info['id'],
        easypost_rate=rate_info['rate'],
        easypost_api_response=address_data['easypost_api_response'],

        payment_service=payment_service,
        payment_confirmation_dictionary=json.dumps(payment_data, default=lambda x: None),

        cart_base_cost=summary_data['information_LOD'][0]['cart_cost_USD'],
        cart_shipping_cost=summary_data['information_LOD'][0]['shipping_cost_USD'],
        cart_total_cost=summary_data['information_LOD'][0]['total_cost_USD'],

    )

    return purchase_history_data_dict


