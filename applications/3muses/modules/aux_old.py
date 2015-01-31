import string
import random

def get_env_var(service, test_or_live, key):
	import os, ast

	## Assume that you are running on herkou first
	try:
		KEY=os.environ[key]

	## If that fails, assume you are running locally and look for key in a text file
	except KeyError:
		with open('/home/wantsomechocolate/Code/API Info/api_keys.txt','r') as fh:
			text=fh.read()
			api_keys=ast.literal_eval(text)

		KEY=api_keys[service][test_or_live][key]

	return KEY



def id_generator(size=16, chars=string.ascii_uppercase + string.digits):

	return ''.join(random.choice(chars) for _ in range(size))


def paypal_create_payment_dict(
		intent='sale', 
		payment_method='paypal', 
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


	## Prepare and add the payer_dict
	payer_dict={}
	payer_dict['payment_method']=payment_method
	payment_dict['payer']=payer_dict


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

	transactions_dict['amount']=amount_dict
	transactions_dict['description']=transaction_description
	transactions_dict['invoice_number']=invoice_number



	item_list_dict=items_paypal_list_of_dicts

	return payment_dict




{   'intent': 'sale',

    'payer': {'payment_method': 'paypal'},

    'redirect_urls': {'cancel_url': 'https://threemusesglass.herokuapp.com',
                      'return_url': 'https://threemusesglass.herokuapp.com/paypal_webhooks'
                     },

    'transactions': [   {   'amount': {   'currency': 'USD',

                                          'details': {   'shipping': '2.00',
                                                         'subtotal': '40.00'},

                                          'total': '42.00'
                                      },

                            'description': 'Purchase from ThreeMusesGlass',

                            'invoice_number': 'OOH7FQWIP6WEZNEU',

                            'item_list': 
                            		{'items':
                            			[   {   'currency': 'USD',
                                                 'description': 'Description of item',
                                                 'name': 'eCig Drip Tip',
                                                 'price': '20.00',
                                                 'quantity': '1'},

                                             {   'currency': 'USD',
                                                 'description': 'Description of item',
                                                 'name': 'eCig Drip Tip Black',
                                                 'price': '20.00',
                                                 'quantity': '1'}
                                         ]
                                    }
                        }
                    ]

}