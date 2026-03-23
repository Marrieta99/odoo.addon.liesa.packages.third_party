# Copyright © 2022 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    feed_gtin = fields.Char(string='GTIN', help='Global Trade Item Number')
    feed_mpn = fields.Char(string='MPN', help='Manufacturer Part Number')
    feed_isbn = fields.Char(string='ISBN', help='International Standard Book Number')
    feed_pzn = fields.Char(string='PZN', help='Pharma Central Number')
    feed_asin = fields.Char(string='ASIN', help='Amazon Standard Identification Number')
