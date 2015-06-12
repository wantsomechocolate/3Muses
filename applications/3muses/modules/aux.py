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
    payment_invoice_number,
    summary_data,
    ):

    import json
    import easypost

    ## easypost_response=json.loads(address_data['easypost_api_response'])
    easypost_response=easypost.Shipment.retrieve(address_data['easypost_shipping_id'])

    rates=easypost_response['rates']

    default_rate=address_data['easypost_default_shipping_rate_id']

    rate_info={}

    for rate in rates:
        if rate['id']==default_rate:
            rate_info=rate


    purchase_history_data_dict=dict(

        # session_id_3muses=session_data.session_id_3muses,
        # session_db_table=session_data.session_db_table,
        session_db_record_id=session_data.session_db_record_id,

        muses_id=user_data.id,
        muses_email_address=user_data.email,
        # muses_name=user_data.first_name,

        shipping_name_first=address_data['first_name'],
        shipping_name_last=address_data['last_name'],
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
        #easypost_api_response=address_data['easypost_api_response'],

        payment_service=payment_service,
        payment_confirmation_id=payment_data.id,
        payment_invoice_number=payment_invoice_number,

        cart_base_cost=summary_data['information_LOD'][0]['cart_cost_USD'],
        cart_shipping_cost=summary_data['information_LOD'][0]['shipping_cost_USD'],
        cart_total_cost=summary_data['information_LOD'][0]['total_cost_USD'],

    )

    return purchase_history_data_dict


def table_generation(grid_header_list, grid_row_lists, basename):

    from gluon.html import DIV
    
    grid=DIV()

    grid['_class']=str(basename)+'_grid_container'

    if grid_header_list!=None:

        grid_header_row=DIV()

        grid_header_row['_class']=str(basename)+'_grid_header_row grid_header_row'

        for i in range(len(grid_header_list)):

            grid_header_row.append(DIV(DIV(grid_header_list[i]), _class=str(basename)+"_grid_header_cell grid_header_cell "+str(basename)+"_grid_col grid_col "+str(basename)+"_grid_col_"+str(i+1)))
        
        grid.append(grid_header_row)

    else:

        pass

    for grid_row_list in grid_row_lists:

        grid_table_row=DIV(_class=str(basename)+"_grid_table_row grid_table_row")

        for i in range(len(grid_row_list)):

            grid_table_row.append(DIV(grid_row_list[i],_class=str(basename)+"_grid_table_cell grid_table_cell "+str(basename)+"_grid_col grid_col "+str(basename)+"_grid_col_"+str(i+1)))

        grid.append(grid_table_row)

    return grid




def generate_confirmation_email_receipt_context(
    muses_email_address=None, 
    purchase_history_data_row=None,
    purchase_history_products_rows=None,
    ):

    import stripe
    import paypalrestsdk


    ###########################################
    #########-----PRODUCT INFORMATION-----#####
    ###########################################
    product_header_row=['Product','Total Weight (oz)','Total Cost($)']
    product_table_row_LOL=[]
    product_total_weight=0
    product_total_cost=0

    ## change this so that you don't have to go into the product database to get this data
    ## It should all be available in the other purchase history tables. 
    ## I'm doing this because the product table has all editable stuff
    ## And I want a more permanent record of the transaction. 
    for row in purchase_history_products_rows:
        #product_data=db(db.product.id==row.product_id).select().first()

        line_item_weight_oz=int(row.product_qty)*int(row.weight_oz)
        line_item_cost_usd=int(row.product_qty)*int(row.cost_USD)

        product_table_row=[
            row.product_name,
            line_item_weight_oz,
            line_item_cost_usd,
        ]

        product_total_weight+=line_item_weight_oz
        product_total_cost+=line_item_cost_usd

        product_table_row_LOL.append(product_table_row)

    product_totals_row=['Total',product_total_weight,product_total_cost,]

    product_table_row_LOL.append(product_totals_row)

    confirmation_product_grid=table_generation(product_header_row,product_table_row_LOL,'confirmation_product')



    ###########################################
    #########-----ADDRESS INFORMATION-----#####
    ###########################################
    address_header_row=['Street Address Info', 'Local Address Info', 'Country']
    address_table_row_LOL=[[
        purchase_history_data_row.shipping_street_address_line_1+" "+purchase_history_data_row.shipping_street_address_line_2,
        purchase_history_data_row.shipping_municipality+", "+purchase_history_data_row.shipping_administrative_area+" "+purchase_history_data_row.shipping_postal_code,
        purchase_history_data_row.shipping_country,
    ]]

    confirmation_address_grid=table_generation(address_header_row,address_table_row_LOL,"confirmation_address")



    ###########################################
    #########-----SHIPPING INFORMATION----#####
    ###########################################
    shipping_header_row=['Carrier-Rate', 'Shipping Weight (Oz)', 'Estimated Shipping Cost ($)']
    shipping_table_row_LOL=[[
        purchase_history_data_row.easypost_shipping_carrier + " - " + purchase_history_data_row.easypost_shipping_service,
        product_total_weight,
        purchase_history_data_row.easypost_rate,
    ]]

    confirmation_shipping_grid=table_generation(shipping_header_row,shipping_table_row_LOL,"confirmation_shipping")


    ###########################################
    #########-----PAYMENT INFORMATION-----#####
    ###########################################
    print "checking payment method"
    if purchase_history_data_row['payment_service']=='stripe':

        print "retrieving payment info from stripe"
        payment_information=stripe.Charge.retrieve(purchase_history_data_row['payment_confirmation_id'])

        print "checking to see if payment object is card"
        if payment_information['source']['object']=='card':
            card_header_row=['Stripe Email', 'Brand-Last4', 'Expiration(mm/yyyy)']

            card_table_row_LOL=[[
                str(payment_information['source']['name']),
                str(payment_information['source']['brand']) + " - " + str(payment_information['source']['last4']),
                str(payment_information['source']['exp_month']) + " / " + str(payment_information['source']['exp_year']),
            ]]


        elif payment_information['source']['object']=='bitcoin_receiver':

            print "Checking to see if payment object is bitcoin_receiver"

            card_header_row=['Stripe Email', 'Bitcoin Metric1', 'Bitcoin Metric2']

            card_table_row_LOL=[[
                str(payment_information['source']['email']), 
                "Metric1", 
                "Metric2",
                #str(payment_information['source']['brand']),
                #str(payment_information['source']['exp_month']),
            ]]

        else:

            print "looks like it wasn't"

            card_header_row=['Stripe Email', 'Bitcoin Metric1', 'Bitcoin Metric2']

            card_table_row_LOL=[[
                str(payment_information['source']['object']), 
                "Metric1", 
                "Metric2",
                #str(payment_information['source']['brand']),
                #str(payment_information['source']['exp_month']),
            ]]

        confirmation_card_grid=table_generation(card_header_row,card_table_row_LOL,"confirmation_card")



    elif purchase_history_data_row['payment_service']=='paypal':

        payment_information=paypalrestsdk.Payment.find(purchase_history_data_row.payment_confirmation_id)

        ##Paypal Info
        card_header_row=['Paypal Name', 'Paypal Email', 'Paypal Invoice Number']
        card_table_row_LOL=[[
            payment_information['payer']['payer_info']['first_name']+payment_information['payer']['payer_info']['last_name'],
            payment_information['payer']['payer_info']['email'],
            'invoice_number',
        ]]

        confirmation_card_grid=table_generation(card_header_row,card_table_row_LOL,"confirmation_card")



    ###########################################
    #########-----SUMMARY INFORMATION-----#####
    ###########################################
    summary_header_row=['Shipping Cost ($)', 'Product Cost ($)', 'Total Cost ($)']
    summary_table_row_LOL=[[
        purchase_history_data_row.easypost_rate,
        product_total_cost,
        float(purchase_history_data_row.easypost_rate)+product_total_cost,
    ]]

    confirmation_summary_grid=table_generation(summary_header_row,summary_table_row_LOL,"confirmation_summary")


    ###########################################
    #########-------HTML GENERATION-------#####
    ###########################################
    # final_div=DIV(_class="muses_pay")
    # final_div.append(DIV("Product Details",_class="confirmation_heading"))
    # final_div.append(confirmation_product_grid)
    # final_div.append(DIV("Address Details",_class="confirmation_heading"))
    # final_div.append(confirmation_address_grid)
    # final_div.append(DIV("Shipping Details",_class="confirmation_heading"))
    # final_div.append(confirmation_shipping_grid)
    # final_div.append(DIV("Payment Details",_class="confirmation_heading"))
    # final_div.append(confirmation_card_grid)
    # final_div.append(DIV("Summary",_class="confirmation_heading"))
    # final_div.append(confirmation_summary_grid)


    # final_div_html=final_div.xml()


    email_icons=dict(
        products_icon_url="https://s3.amazonaws.com/threemusesglass/icons/ProductIcon.png",
        address_icon_url="https://s3.amazonaws.com/threemusesglass/icons/AddressIcon.png",
        shipping_icon_url="https://s3.amazonaws.com/threemusesglass/icons/ShippingIcon.png",
        payment_icon_url="https://s3.amazonaws.com/threemusesglass/icons/PaymentIcon.png",
        summary_icon_url="https://s3.amazonaws.com/threemusesglass/icons/SummaryIcon.png",
        )

    #purchase_history_dict
    #purchase_history_products_LOD

    ## Try to overwrite the date with a string and convert back later using dateutil if necessary

    receipt_context=dict(
        email_icons=email_icons,
        #purchase_details=purchase_history_dict,
        #product_details=purchase_history_products_LOD,
        product_info=product_table_row_LOL,
        address_info=address_table_row_LOL,
        shipping_info=shipping_table_row_LOL,
        card_info=card_table_row_LOL,
        summary_info=summary_table_row_LOL,
        )

    #receipt_message_html = response.render('receipt.html', receipt_context)
    #receipt_message_html = response.render('default/receipt.html', receipt_context)


    #return receipt_message_html
    return receipt_context


def retrieve_cart_contents(auth,db,is_active=True):

    # cart=db((db.muses_cart.user_id==auth.user_id)&(db.muses_cart.is_active==True)).select()
    if is_active:
        cart=db((db.muses_cart.user_id==auth.user_id)&(db.muses_cart.is_active==True)).select()
    else:
        cart=db(db.muses_cart.user_id==auth.user_id).select()

    return cart


## the number of days is sometimes 0 or null
def shipping_date_from_integer(number_of_days,shipping_method,shipping_company,shipping_country):

    from datetime import datetime

    shipping_time_estimates=dict(
                            USPS=dict(
                                regular_ground=dict(
                                    number_of_days=7
                                    )
                                )
                            )

    holidays=[datetime(2015,4,19)]

    handling_days=1

    try:
        if number_of_days>0 and isintance(number_of_days,int):
            disclaimer="Shipping dates are estimations and can be off by a day or two."

        else:
            number_of_days=shipping_time_estimates[shipping_company][shipping_method]['number_of_days']
            disclaimer="Shipping date calculation could not be performed, so a lookup was used to provide estimated delivery date based on the deliverer and the shipping option chosen."



    except KeyError:
        disclaimer="Shipping date calculation could not be performed for the current shipping option, the date here is an upper bound and does not represent actual delivery date."
        ## This should be the max possible estimated shipping date for the given shipping_company and country
        number_of_days=12


    number_of_days+=handling_days
    business_days_to_add = number_of_days
    current_date = datetime.now()
    transient_date=current_date
    for i in range(number_of_days):
        if current_date.weekeday>=5 or current_date in holdiays:
            pass
        else:
            current_date += datetime.timedelta(days=1)
        
    
    shipping_estimate_info_dict=dict(estimated_shipping_date=current_date,disclaimer=disclaimer)

    return shipping_estimate_info_dict




