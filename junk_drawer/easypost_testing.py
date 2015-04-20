import easypost
import os
easypost.api_key=os.environ['EASYPOST_KEY']
shipment=easypost.Shipment.retrieve('shp_sq2zuZ8d')
