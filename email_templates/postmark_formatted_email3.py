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
html_email='<html><body><p>There should be an image here</p><img src="http://i.imgur.com/eT8ogahb.jpg"></body></html>'

## Send the message
message = PMMail(api_key=POSTMARK_API_KEY,
    subject="Testing Formatted Emails",
    sender="Rebecca@3musesglass.com",
    to='wantsomechocolate@gmail.com',
    html_body=html_email,
    tag="Test",
    #attachments=[('bacon.png','iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAAyklEQVR42mNgGAUjAbAOlMVBQBwKxDF0wiC7FEAWXwHiL0D8n04YZNcMkMW/gfgTEDfQCYPs+gqy+B8QP6Nj1D6F+nyEWvwTiA/TCf9Atvj/AOARavGAp2pQuS2BBXPQ2mIrHMESOxgtZoXq04HyRaF8WShfBcrnpbbFElA1R6D8GCi/AcpfCOVb47NYFYgXYcHWeCzmh6qpQXI8iB8I5adB+aqDpsj8BMV1dMIfYdXi9AFoCIDsZFAE4jBoAqIHBtklP9rUHQU0AwD8eibVIMZdgwAAAABJRU5ErkJggg==','image/png')]
)

message.send()
