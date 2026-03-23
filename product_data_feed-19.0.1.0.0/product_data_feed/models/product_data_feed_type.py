from odoo import fields, models


class ProductDataFeedType(models.Model):
    _name = "product.data.feed.type"
    _description = 'Types of Product Data Feeds'

    name = fields.Char(required=True)
    recipient_id = fields.Many2one(
        comodel_name='product.data.feed.recipient',
        string='Recipient',
        ondelete='cascade',
        required=True,
    )

    _name_recipient_unique = models.Constraint(
        'unique (name, recipient_id)',
        'Data feed type must be unique per recipient.'
    )
