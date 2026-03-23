from odoo import models, fields


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    google_category_id = fields.Many2one(comodel_name='product.google.category', string='Google Category')
