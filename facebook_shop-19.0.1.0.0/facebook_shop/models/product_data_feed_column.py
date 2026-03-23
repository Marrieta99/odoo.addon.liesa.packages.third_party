# Copyright © 2025 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License OPL-1 (https://www.odoo.com/documentation/19.0/legal/licenses.html).

from odoo import models


class ProductDataFeedColumn(models.Model):
    _inherit = "product.data.feed.column"

    def _get_value(self, product):
        self.ensure_one()
        value = super(ProductDataFeedColumn, self)._get_value(product)
        if not self.feed_id.recipient_is_facebook_shop:
            return value

        if self.name == 'google_product_category':
            # Allow using the Google category specified in a public product category,
            # to avoid setting a Google category for each product
            google_category = self._get_google_category(product)
            if google_category:
                value = google_category.code

        return value
