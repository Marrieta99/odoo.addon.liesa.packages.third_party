# Copyright © 2022 Garazd Creation (https://garazd.biz)
# @author: Yurii Razumovskyi (support@garazd.biz)
# @author: Iryna Razumovska (support@garazd.biz)
# License OPL-1 (https://www.odoo.com/documentation/master/legal/licenses.html#odoo-apps).

# flake8: noqa: E501

{
    'name': 'Odoo Google Shopping | Google Merchant Center Next',
    'version': '19.0.1.1.0',
    'category': 'eCommerce',
    'author': 'Garazd Creation',
    'website': 'https://garazd.biz/blog/odoo-e-commerce/odoo-google-shopping',
    'license': 'OPL-1',
    'summary': 'Odoo Google Merchant Center Integration | Google Shopping | GMC | Google Feed | Product Data Feed | Free listings | Shopping ads | Odoo Google Shopping feed | Merchant Center Next',
    'images': ['static/description/banner.gif', 'static/description/icon.png'],
    'live_test_url': 'https://garazd.biz/r/FjE',
    'depends': [
        'product_data_feed',
        'product_data_feed_brand',
        'product_data_feed_number',
    ],
    'data': [
        'data/product_data_feed_recipient_data.xml',
        'data/product_data_feed_data.xml',
        'data/product_data_feed_column_value_data.xml',
        'data/product_data_feed_column_data.xml',
        'views/product_template_views.xml',
    ],
    'price': 111.80,
    'currency': 'EUR',
    'support': 'support@garazd.biz',
    'application': True,
    'installable': True,
    'auto_install': False,
}
