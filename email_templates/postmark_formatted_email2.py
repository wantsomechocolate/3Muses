## Imports
from postmark import PMMail
import os, ast

## Get the API Key
try:
    POSTMARK_API_KEY=os.environ['POSTMARK_API_KEY']
except KeyError:

    with open('/home/wantsomechocolate/Code/API Info/api_keys.txt','r') as fh:
        text=fh.read()
        api_keys=ast.literal_eval(text)

    POSTMARK_API_KEY=api_keys['postmark']['test']['POSTMARK_API_KEY']

## Make the html
#html_email="<div background-color=pink>Is pink here again?</div>"
html_email="""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns="http://www.w3.org/1999/xhtml" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;">
  <head>
    <meta name="viewport" content="width=device-width" />
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>ThreeMusesGlass</title>
  </head>
  <body bgcolor="#f6f6f6" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; -webkit-font-smoothing: antialiased; -webkit-text-size-adjust: none; width: 100% !important; height: 100%; margin: 0; padding: 0;">&#13;
&#13;
<!-- body -->&#13;
<table class="body-wrap" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 100%; margin: 0; padding: 20px;"><tr style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;"><td style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;"></td>&#13;
		<td class="container" bgcolor="#FFFFFF" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; display: block !important; max-width: 600px !important; clear: both !important; margin: 0 auto; padding: 20px; border: 1px solid #f0f0f0;">&#13;
&#13;
			<!-- content -->&#13;
			<div class="content" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; max-width: 600px; display: block; margin: 0 auto; padding: 0;">&#13;
			<table style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 100%; margin: 0; padding: 0;"><tr style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;"><td style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;">&#13;
						<h2 style="font-family: 'Helvetica Neue', Helvetica, Arial, 'Lucida Grande', sans-serif; font-size: 28px; line-height: 1.2; color: #000; font-weight: 200; margin: 40px 0 10px; padding: 0;">Thank you for shopping with ThreeMusesGlass</h2>&#13;
						<h5 style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;">Below are the details of your order:</h5>&#13;
						&#13;
&#13;
						<h3 class="header_text" style="font-family: 'Helvetica Neue', Helvetica, Arial, 'Lucida Grande', sans-serif; font-size: 22px; line-height: 1.2; color: #000; font-weight: 200; margin: 40px 0 10px; padding: 0;">&#13;
&#13;
							<img class="header_icon" src="https://s3.amazonaws.com/threemusesglass/icons/ProductIcon.png" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; max-width: 100%; width: 30px; height: 30px; margin: 0; padding: 0;" />&#13;
&#13;
							Product Details&#13;
&#13;
						</h3>&#13;
&#13;
&#13;
&#13;
						<table class="summary_table" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 100%; border-top-style: solid; margin: 0; padding: 0;"><tr style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; background-color: #F7A3F7; margin: 0; padding: 0;" bgcolor="#F7A3F7"><th class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 33%; margin: 0; padding: 10px 0;">&#13;
									<h4 style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;">Product</h4>&#13;
								</th>&#13;
								<th class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 33%; margin: 0; padding: 10px 0;">&#13;
									<h4 style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;">Total Weight (oz)</h4>&#13;
								</th>&#13;
								<th class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 33%; margin: 0; padding: 10px 0;">&#13;
									<h4 style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;">Total Cost ($)</h4>&#13;
								</th>&#13;
							</tr><tr style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; background-color: #FAE3FA; margin: 0; padding: 0;" bgcolor="#FAE3FA"><td class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; text-align: center; width: 33%; margin: 0; padding: 10px 0 0px;" align="center">&#13;
									<p style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; font-weight: normal; margin: 0 0 10px; padding: 0;">Product Name</p>&#13;
								</td>&#13;
								<td class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; text-align: center; width: 33%; margin: 0; padding: 10px 0 0px;" align="center">&#13;
									<p style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; font-weight: normal; margin: 0 0 10px; padding: 0;">3</p>&#13;
								</td>&#13;
								<td class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; text-align: center; width: 33%; margin: 0; padding: 10px 0 0px;" align="center">&#13;
									<p style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; font-weight: normal; margin: 0 0 10px; padding: 0;">$25.00</p>&#13;
								</td>&#13;
							</tr><tr style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; background-color: #FAD4FA; margin: 0; padding: 0;" bgcolor="#FAD4FA"><td class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; text-align: center; width: 33%; margin: 0; padding: 10px 0 0px;" align="center">&#13;
									<p style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; font-weight: normal; margin: 0 0 10px; padding: 0;">Total</p>&#13;
								</td>&#13;
								<td class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; text-align: center; width: 33%; margin: 0; padding: 10px 0 0px;" align="center">&#13;
									<p style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; font-weight: normal; margin: 0 0 10px; padding: 0;">3</p>&#13;
								</td>&#13;
								<td class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; text-align: center; width: 33%; margin: 0; padding: 10px 0 0px;" align="center">&#13;
									<p style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; font-weight: normal; margin: 0 0 10px; padding: 0;">$25.00</p>&#13;
								</td>&#13;
							</tr></table><h3 class="header_text" style="font-family: 'Helvetica Neue', Helvetica, Arial, 'Lucida Grande', sans-serif; font-size: 22px; line-height: 1.2; color: #000; font-weight: 200; margin: 40px 0 10px; padding: 0;">&#13;
&#13;
							<img class="header_icon" src="https://s3.amazonaws.com/threemusesglass/icons/AddressIcon.png" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; max-width: 100%; width: 30px; height: 30px; margin: 0; padding: 0;" />&#13;
&#13;
							Address Details&#13;
&#13;
						</h3>&#13;
&#13;
						<table class="summary_table" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 100%; border-top-style: solid; margin: 0; padding: 0;"><tr style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; background-color: #F7A3F7; margin: 0; padding: 0;" bgcolor="#F7A3F7"><th class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 33%; margin: 0; padding: 10px 0;">&#13;
									<h4 style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;">Street Address Info</h4>&#13;
								</th>&#13;
								<th class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 33%; margin: 0; padding: 10px 0;">&#13;
									<h4 style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;">Local Address Info</h4>&#13;
								</th>&#13;
								<th class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 33%; margin: 0; padding: 10px 0;">&#13;
									<h4 style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;">Country</h4>&#13;
								</th>&#13;
							</tr><tr style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; background-color: #FAE3FA; margin: 0; padding: 0;" bgcolor="#FAE3FA"><td class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; text-align: center; width: 33%; margin: 0; padding: 10px 0 0px;" align="center">&#13;
									<p style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; font-weight: normal; margin: 0 0 10px; padding: 0;">123 Street Apt F12</p>&#13;
								</td>&#13;
								<td class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; text-align: center; width: 33%; margin: 0; padding: 10px 0 0px;" align="center">&#13;
									<p style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; font-weight: normal; margin: 0 0 10px; padding: 0;">Croton Falls, NY 09813</p>&#13;
								</td>&#13;
								<td class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; text-align: center; width: 33%; margin: 0; padding: 10px 0 0px;" align="center">&#13;
									<p style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; font-weight: normal; margin: 0 0 10px; padding: 0;">United States</p>&#13;
								</td>&#13;
							</tr></table><h3 class="header_text" style="font-family: 'Helvetica Neue', Helvetica, Arial, 'Lucida Grande', sans-serif; font-size: 22px; line-height: 1.2; color: #000; font-weight: 200; margin: 40px 0 10px; padding: 0;">&#13;
&#13;
							<img class="header_icon" src="https://s3.amazonaws.com/threemusesglass/icons/ShippingIcon.png" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; max-width: 100%; width: 30px; height: 30px; margin: 0; padding: 0;" />&#13;
&#13;
							Shipping Details&#13;
&#13;
						</h3>&#13;
&#13;
						&#13;
						<table class="summary_table" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 100%; border-top-style: solid; margin: 0; padding: 0;"><tr style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; background-color: #F7A3F7; margin: 0; padding: 0;" bgcolor="#F7A3F7"><th class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 33%; margin: 0; padding: 10px 0;">&#13;
									<h4 style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;">Carrier-Rate</h4>&#13;
								</th>&#13;
								<th class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 33%; margin: 0; padding: 10px 0;">&#13;
									<h4 style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;">Shipping Weight (Oz)</h4>&#13;
								</th>&#13;
								<th class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 33%; margin: 0; padding: 10px 0;">&#13;
									<h4 style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;">Estimated Shipping Cost</h4>&#13;
								</th>&#13;
							</tr><tr style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; background-color: #FAE3FA; margin: 0; padding: 0;" bgcolor="#FAE3FA"><td class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; text-align: center; width: 33%; margin: 0; padding: 10px 0 0px;" align="center">&#13;
									<p style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; font-weight: normal; margin: 0 0 10px; padding: 0;">USPS - First</p>&#13;
								</td>&#13;
								<td class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; text-align: center; width: 33%; margin: 0; padding: 10px 0 0px;" align="center">&#13;
									<p style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; font-weight: normal; margin: 0 0 10px; padding: 0;">3</p>&#13;
								</td>&#13;
								<td class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; text-align: center; width: 33%; margin: 0; padding: 10px 0 0px;" align="center">&#13;
									<p style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; font-weight: normal; margin: 0 0 10px; padding: 0;">1.93</p>&#13;
								</td>&#13;
							</tr></table><h3 class="header_text" style="font-family: 'Helvetica Neue', Helvetica, Arial, 'Lucida Grande', sans-serif; font-size: 22px; line-height: 1.2; color: #000; font-weight: 200; margin: 40px 0 10px; padding: 0;">&#13;
&#13;
							<img class="header_icon" src="https://s3.amazonaws.com/threemusesglass/icons/PaymentIcon.png" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; max-width: 100%; width: 30px; height: 30px; margin: 0; padding: 0;" />&#13;
&#13;
							Payment Details&#13;
&#13;
						</h3>&#13;
&#13;
&#13;
						&#13;
						<table class="summary_table" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 100%; border-top-style: solid; margin: 0; padding: 0;"><tr style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; background-color: #F7A3F7; margin: 0; padding: 0;" bgcolor="#F7A3F7"><th class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 33%; margin: 0; padding: 10px 0;">&#13;
									<h4 style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;">Name</h4>&#13;
								</th>&#13;
								<th class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 33%; margin: 0; padding: 10px 0;">&#13;
									<h4 style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;">Brand-Last4 (Oz)</h4>&#13;
								</th>&#13;
								<th class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 33%; margin: 0; padding: 10px 0;">&#13;
									<h4 style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;">Expiration (MM/YYYY)</h4>&#13;
								</th>&#13;
							</tr><tr style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; background-color: #FAE3FA; margin: 0; padding: 0;" bgcolor="#FAE3FA"><td class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; text-align: center; width: 33%; margin: 0; padding: 10px 0 0px;" align="center">&#13;
									<p style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; font-weight: normal; margin: 0 0 10px; padding: 0;">Mr. John Doe</p>&#13;
								</td>&#13;
								<td class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; text-align: center; width: 33%; margin: 0; padding: 10px 0 0px;" align="center">&#13;
									<p style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; font-weight: normal; margin: 0 0 10px; padding: 0;">Visa - 4242</p>&#13;
								</td>&#13;
								<td class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; text-align: center; width: 33%; margin: 0; padding: 10px 0 0px;" align="center">&#13;
									<p style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; font-weight: normal; margin: 0 0 10px; padding: 0;">12 / 2020</p>&#13;
								</td>&#13;
							</tr></table><h3 class="header_text" style="font-family: 'Helvetica Neue', Helvetica, Arial, 'Lucida Grande', sans-serif; font-size: 22px; line-height: 1.2; color: #000; font-weight: 200; margin: 40px 0 10px; padding: 0;">&#13;
&#13;
							<img class="header_icon" src="https://s3.amazonaws.com/threemusesglass/icons/SummaryIcon.png" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; max-width: 100%; width: 30px; height: 30px; margin: 0; padding: 0;" />&#13;
&#13;
							Summary&#13;
&#13;
						</h3>&#13;
						&#13;
						<table class="summary_table" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 100%; border-top-style: solid; margin: 0; padding: 0;"><tr style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; background-color: #F7A3F7; margin: 0; padding: 0;" bgcolor="#F7A3F7"><th class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 33%; margin: 0; padding: 10px 0;">&#13;
									<h4 style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;">Shipping Cost</h4>&#13;
								</th>&#13;
								<th class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 33%; margin: 0; padding: 10px 0;">&#13;
									<h4 style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;">Product Cost</h4>&#13;
								</th>&#13;
								<th class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 33%; margin: 0; padding: 10px 0;">&#13;
									<h4 style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;">Total Cost</h4>&#13;
								</th>&#13;
							</tr><tr style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; background-color: #FAE3FA; margin: 0; padding: 0;" bgcolor="#FAE3FA"><td class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; text-align: center; width: 33%; margin: 0; padding: 10px 0 0px;" align="center">&#13;
									<p style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; font-weight: normal; margin: 0 0 10px; padding: 0;">1.93</p>&#13;
								</td>&#13;
								<td class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; text-align: center; width: 33%; margin: 0; padding: 10px 0 0px;" align="center">&#13;
									<p style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; font-weight: normal; margin: 0 0 10px; padding: 0;">40</p>&#13;
								</td>&#13;
								<td class="padding" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; text-align: center; width: 33%; margin: 0; padding: 10px 0 0px;" align="center">&#13;
									<p style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; font-weight: normal; margin: 0 0 10px; padding: 0;">41.93</p>&#13;
								</td>&#13;
							</tr></table><p style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; font-weight: normal; margin: 0 0 10px; padding: 0;"> </p>&#13;
&#13;
						<p style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; font-weight: normal; margin: 0 0 10px; padding: 0;">Thanks, have a lovely day. Come back soon!</p>&#13;
					</td>&#13;
				</tr></table></div>&#13;
			<!-- /content -->&#13;
			&#13;
		</td>&#13;
		<td style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;"></td>&#13;
	</tr></table><!-- /body --><!-- footer --><table class="footer-wrap" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 100%; clear: both !important; margin: 0; padding: 0;"><tr style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;"><td style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;"></td>&#13;
		<td class="container" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; display: block !important; max-width: 600px !important; clear: both !important; margin: 0 auto; padding: 0;">&#13;
			&#13;
			<!-- content -->&#13;
			<div class="content" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; max-width: 600px; display: block; margin: 0 auto; padding: 0;">&#13;
				<table style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; width: 100%; margin: 0; padding: 0;"><tr style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;"><td align="center" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;">&#13;
							<p style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 12px; line-height: 1.6; color: #666; font-weight: normal; margin: 0 0 10px; padding: 0;">You have recieved this email because a purchase was made at ThreeMusesGlass with this email address. If you think this email was sent in error: <a href="#" style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; color: #999; margin: 0; padding: 0;"><unsubscribe style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;">Click Here</unsubscribe></a>.&#13;
							</p>&#13;
						</td>&#13;
					</tr></table></div>&#13;
			<!-- /content -->&#13;
			&#13;
		</td>&#13;
		<td style="font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 100%; line-height: 1.6; margin: 0; padding: 0;"></td>&#13;
	</tr></table><!-- /footer --></body>
</html>
"""

## Send the message
message = PMMail(api_key=POSTMARK_API_KEY,
    subject="Testing Formatted Emails",
    sender="James@3musesglass.com",
    #to='wantsomechocolate@gmail.com',
    #to='jmcglynn@codegreensolutions.com',
    to='rmcglynn01@gmail.com',
    html_body=html_email,
    tag="Test")
message.send()
