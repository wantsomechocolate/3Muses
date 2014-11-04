# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B('Home'),
                  _class="brand",_href=URL('default', 'index'))
#response.title = request.application.replace('_',' ').title()
response.title = '3MusesGlass'
response.subtitle = 'Hand-Crafted Glass Pieces'

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Rebecca McGlynn <rmcglynn01@gmail.com>'
response.meta.keywords = 'glass, three, muses, threemuses, etsy, ecig, vape'
response.meta.generator = 'Three Muses Glass'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [

]

DEVELOPMENT_MENU = True

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller
    # useful links to internal and external resources

    categories=db(db.categories.is_active==True).select()
    category_names=[]
    category_names.append((T('All Categories'),False,URL('categories')))
    for row in categories:
      category_names.append((T(row.category_name),False,URL('display/'+str(row.id))))

    admin_pages_li=[
    (T('Manage Products'),False,URL('manage_products')),
    (T('Manage Product Images'),False,URL('manage_product_images')),
    (T('Manage Categories'),False,URL('manage_categories')),
    (T('Manage Landing Page'),False,URL('manage_landing_page_images')),
    ]

    response.menu += [
      (SPAN("Navigation"), False, '', [
        (T('Product Lines'), False, None, category_names),
        (T('3Muses on Etsy'), False, 'https://www.etsy.com/shop/3MusesGlass', None),
        (T('Meet The Artist'),False, URL('artist')),
        ],
      )]

    if auth.has_membership('admin'):
      response.menu += [
        (SPAN("Admin Pages"), False, None, admin_pages_li),
        ]
    else:
      pass


if DEVELOPMENT_MENU: _()

if "auth" in locals(): auth.wikimenu() 
