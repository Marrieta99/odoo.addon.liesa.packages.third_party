# Copyright © 2020 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License OPL-1 (https://www.odoo.com/documentation/14.0/legal/licenses.html#odoo-apps).

import hashlib
import logging
import uuid

from typing import List
from markupsafe import Markup

from odoo.addons.base.models.res_partner import _lang_get, _tz_get
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo import _, api, fields, models
from .product_data_feed_column import ProductDataFeedColumn

_logger = logging.getLogger(__name__)


class ProductDataFeed(models.Model):
    _name = "product.data.feed"
    _inherit = ['mail.thread']
    _description = 'Product Data Feed'
    _order = 'sequence'

    @api.model
    def _get_default_model_domain(self):
        return [('is_published', '=', True)]

    @api.model
    def _default_filename(self):
        return 'feed-%s' % str(uuid.uuid4())[:4]

    @api.model
    def _default_sequence(self):
        return (self.search([], order='sequence desc', limit=1).sequence or 1) + 1

    sequence = fields.Integer(default=_default_sequence)
    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    is_template = fields.Boolean(string='Template', copy=False)
    recipient_id = fields.Many2one(
        comodel_name='product.data.feed.recipient',
        string='Recipient',
        ondelete='cascade',
        required=True,
        tracking=True,
    )
    type_id = fields.Many2one(
        comodel_name='product.data.feed.type',
        ondelete='cascade',
        tracking=True,
    )
    parent_feed_id = fields.Many2one(comodel_name='product.data.feed', readonly=True)
    website_ids = fields.Many2many(
        comodel_name='website',
        string='Websites',
        help='Allow this data feed for selected websites. Allow for all if not set.',
    )
    url = fields.Char(string='Feed URL', readonly=True, compute='_compute_url')
    use_token = fields.Boolean(tracking=True)
    access_token = fields.Char(readonly=True)
    file_type = fields.Selection(
        selection=[
            ('csv', 'CSV'),
            ('tsv', 'TSV'),
            ('xml', 'XML'),
        ],
        string='File Format',
        default='csv',
        tracking=True,
    )
    xml_specification = fields.Selection(
        selection=[
            ('rss_2_0', 'RSS 2.0'),
            ('atom_1_0', 'Atom 1.0'),
        ],
        string='Specification',
        tracking=True,
    )
    use_filename = fields.Boolean(
        string='Use a custom file name.',
        help='Use a custom file name for the feed.',
        tracking=True,
    )
    filename = fields.Char(
        string='File Name',
        default=_default_filename,
        tracking=True,
    )
    text_separator = fields.Char(string='Separator', default=',', tracking=True)
    model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Model',
        domain=[('model', 'in', ['product.product', 'product.template'])],
        ondelete='cascade',
        required=True,
        default=lambda self: self.env.ref('product.model_product_template'),
        tracking=True,
    )
    model_name = fields.Char(string='Model Name', related='model_id.model', store=True)
    column_ids = fields.One2many(
        comodel_name='product.data.feed.column',
        inverse_name='feed_id',
        string='Columns',
        readonly=True,
    )
    column_count = fields.Integer(compute='_compute_column_count')
    item_count = fields.Integer(compute='_compute_item_count')
    model_domain = fields.Char(
        string='Item Filter',
        help='The model domain to filter items for the feed.',
        default=_get_default_model_domain,
    )
    availability_type = fields.Selection(
        selection=[
            ('qty_available', 'Quantity On Hand'),
            ('virtual_available', 'Forecast Quantity'),
            ('free_qty', 'Free To Use Quantity'),
        ],
        help='Determine which stock measurement to use to calculate the stock of products.',
        default='qty_available',
        required=True,
        tracking=True,
    )
    stock_location_ids = fields.Many2many(
        comodel_name='stock.location',
        string='Stock Locations',
        domain=[('usage', '=', 'internal')],
        help='Get products only from these stock locations. '
             'Get products from all internal locations if not set.',
    )
    out_of_stock_mode = fields.Selection(
        selection=[
            ('order', 'Available for order'),
            ('out_of_stock', 'Out of stock'),
        ],
        string='Out of stock mode',
        help='Define which availability status should be used for products that are out of stock.',
        default='out_of_stock',
        required=True,
        tracking=True,
    )
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Pricelist',
        ondelete='set null',
        tracking=True,
    )
    sale_pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Sale Pricelist',
        help="Price list with discounted prices.",
        ondelete='set null',
        tracking=True,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        default=lambda self: self.env.user.company_id.currency_id,
        required=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True,
        default=lambda self: self.env.user.company_id,
    )
    currency_position = fields.Selection(
        selection=[
            ('default', 'By default'),
            ('before', 'Before price'),
            ('after', 'After price'),
            ('none', 'Without currency code'),
        ],
        default='default',
        required=True,
    )
    price_include_taxes = fields.Boolean(string='Include Taxes', tracking=True)
    tax_country_id = fields.Many2one(
        string='Country',
        comodel_name='res.country',
        help='The country used to get taxes for prices when taxes is included. '
             'If not specified, all taxes for the current company are used.',
    )
    product_root_category = fields.Char(
        help='Specify a custom root category name for the "product_category" columns.',
    )
    image_resolution = fields.Selection(
        selection=[
            ('1920', 'Up to 1920 px'),
            ('1024', 'Up to 1024 px'),
            ('512', 'Up to 512 px'),
            ('256', 'Up to 256 px'),
            ('128', 'Up to 128 px'),
        ],
        default='1920',
    )
    lang = fields.Selection(
        selection=_lang_get,
        string='Language',
        default=lambda self: self.env.ref('base.user_root').lang,
        help="The language that will be used to translate all feed text values.",
    )
    tz = fields.Selection(
        selection=_tz_get,
        string='Timezone',
        default='UTC',
        required=True,
    )
    warning_messages = fields.Text(readonly=True)
    actual_date = fields.Datetime(string='Actual on', compute='_compute_actual_date')
    content_disposition = fields.Selection(
        selection=[
            ('inline', 'Web Page'),
            ('attachment', 'Attachment'),
        ],
        default='inline',
        required=True,
        tracking=True,
    )
    debug_mode = fields.Boolean(help='Activate extra logging to the Odoo system log.')
    with_traceback = fields.Boolean(
        string='Error Traceback',
        help='Technical field to debug feed generation errors and show full traceback when this option is active. '
             'Typically, it should be deactivated.',
        tracking=True,
    )
    cache_partial_is_enabled = fields.Boolean(compute='_compute_cache_partial_is_enabled')
    do_compress = fields.Boolean(string='Compress', help='Add the feed file to an archive.')
    compress_type = fields.Selection(
        selection=[('zip', 'ZIP'), ('gz', 'GZIP'), ('bz2', 'Bzip2')],
        default='zip',
        help='Archive type for file compression.',
    )
    # Seller Section
    is_seller_section_visible = fields.Boolean(
        compute='_compute_is_seller_section_visible',
        help='Technical field to define if seller section is visible on feed form',
    )
    seller_id = fields.Many2one(
        comodel_name='res.partner',
        default=lambda self: self.env.user.company_id.partner_id
    )
    seller_url = fields.Char(
        default=lambda self: self.seller_id and self.seller_id.website or False,
    )
    seller_privacy_url = fields.Char()
    seller_terms_url = fields.Char()
    seller_return_url = fields.Char()
    seller_return_days = fields.Integer()

    @api.constrains('access_token')
    def _check_access_token(self):
        for feed in self:
            if self.search_count([('use_token', '=', True), ('access_token', '=', feed.access_token)]) > 1:
                raise ValidationError(_('The access token must be unique.'))

    @api.constrains('use_filename', 'filename')
    def _check_filename_unique(self):
        for feed in self:
            if self.search_count([('filename', '=', feed.filename), ('use_filename', '=', True)]) > 1:
                raise ValidationError(_('The feed filename must be unique.'))

    def _show_seller_section(self):
        """
        Display section of feed form depending on recipient.
        Method to override
        """
        self.ensure_one()
        return False

    @api.depends('recipient_id')
    def _compute_is_seller_section_visible(self):
        for feed in self:
            feed.is_seller_section_visible = feed._show_seller_section()

    @api.depends('column_ids')
    def _compute_column_count(self):
        for feed in self:
            feed.column_count = len(feed.column_ids)

    def _compute_actual_date(self):
        for feed in self:
            feed.actual_date = fields.Datetime.now()

    def _compute_item_count(self):
        for feed in self:
            feed.item_count = len(feed._get_items_by_domain())

    @api.onchange('use_token', 'access_token')
    def _onchange_use_token(self):
        for feed in self:
            if feed.use_token and not feed.access_token:
                feed.access_token = feed._generate_access_token()

    @api.model
    def _generate_access_token(self):
        return str(uuid.uuid4())

    def _get_website(self):
        self.ensure_one()
        return self.website_ids[0] if self.website_ids else self.env['website'].browse()

    def _get_base_url(self) -> str:
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='')
        for feed in self.filtered('website_ids'):
            # Operate with the first website only
            website = feed._get_website()
            # Use the specified website domain
            if website.domain:
                base_url = website.get_base_url()
            # Add a language code to URLs to localize
            if feed.lang and len(website.language_ids) > 1:
                lang = self.env['res.lang']._lang_get(feed.lang)
                if lang not in website.language_ids:
                    feed.sudo()._add_warning(_(
                        "The selected language \"%s\" is not available on the \"%s\" website. "
                        "URLs in the feed data don't contain the language code.", lang.name, website.name,
                    ))
                    lang_code = ''
                else:
                    lang_code = '/%s' % lang.url_code
                base_url = f"{base_url}{lang_code}"
        return base_url

    def _get_file_extension(self):
        self.ensure_one()
        return self.file_type if self.file_type != "tsv" else "csv"

    def _get_file_name(self):
        self.ensure_one()
        return f"{self.use_filename and self.filename or 'feed'}.{self._get_file_extension()}"

    def _compute_cache_partial_is_enabled(self):
        for feed in self:
            feed.cache_partial_is_enabled = feed.file_type in ['csv', 'tsv']

    @api.depends('use_token', 'access_token')
    def _compute_url(self):
        for feed in self:
            if feed.use_filename and feed.filename:
                feed_path = f'product_data/{feed.filename}.{feed._get_file_extension()}'
            else:
                feed_path = f'product_data/{feed._origin.id}/feed.{feed._get_file_extension()}'
            token = "?access_token=%s" % feed.access_token if feed.use_token else ""
            feed.url = f'{feed._get_base_url()}/{feed_path}{token}'

    def _get_source_feed(self):
        self.ensure_one()
        return self.parent_feed_id or self

    def get_currency(self, pricelist=None):
        self.ensure_one()
        feed = self._get_source_feed()
        pricelist = pricelist or feed.pricelist_id
        return pricelist and pricelist.currency_id or feed.currency_id

    def _get_availability_value(self, qty: float, column: ProductDataFeedColumn) -> str:
        self.ensure_one()
        feed = self._get_source_feed()
        value = ''
        if column.type == 'special' and column.special_type == 'availability':
            if qty <= 0:
                if feed.out_of_stock_mode == 'order':
                    value = feed.recipient_id.special_avail_order or 'available for order'
                else:
                    value = feed.recipient_id.special_avail_out or 'out of stock'
            else:
                value = feed.recipient_id.special_avail_in or 'in stock'
        return value

    def _xml_get_item_list_tag_name(self) -> str:
        """ Return an XML feed tag name for the item list element. Method to override."""
        self.ensure_one()
        return ''

    def _xml_get_item_tag_name(self) -> str:
        """ Return an XML feed tag name for the item element. Method to override."""
        self.ensure_one()
        return ''

    def _get_items_by_domain(self):
        """Return all records by the feed domain."""
        self.ensure_one()
        feed = self._get_source_feed()
        return self.env[feed.model_name].search(safe_eval(feed.model_domain))

    def _get_items(self):
        """Return feed records. Method to override."""
        self.ensure_one()
        feed = self._get_source_feed()
        return feed._get_items_by_domain()

    def get_items_with_context(self):
        """Get feed products with params in context."""
        self.ensure_one()
        feed = self._get_source_feed()
        return feed._get_items().with_context(lang=feed.lang)

    def _get_product_qty(self, product) -> float:
        self.ensure_one()
        feed = self._get_source_feed()

        # PATCH to fix 'product.template' object has no attribute 'free_qty'
        products = product if feed.model_name == 'product.product' else product.product_variant_ids

        if not feed.stock_location_ids:
            qty = sum(getattr(pv, feed.availability_type) for pv in products)
        else:
            qty = sum(getattr(
                pv.with_context(location=feed.stock_location_ids.ids),
                feed.availability_type,
            ) for pv in products)
        return qty

    def _get_product_image_field_name(self):
        self.ensure_one()
        feed = self._get_source_feed()
        return f"image_{feed.image_resolution if feed.image_resolution else '1024'}"

    @api.model
    def _get_image_checksum(self, image: bytes):
        checksum = ''
        try:
            checksum = hashlib.sha1(image or b'').hexdigest()
        except Exception as e:
            _logger.warning("Image getting checksum error: ", str(e))
        return checksum

    @api.model
    def _escape_text_value(self, value) -> str:
        """Remove double quotes from values for text files."""
        return value.replace('"', '') if isinstance(value, str) else ''

    def _get_text_lines(self, product) -> List[str]:
        """Return a file row with values divided by a separator.
           For special cases we use a list of str as result.
        """
        self.ensure_one()
        values = []
        for column in self.column_ids:
            values.append(self._escape_text_value(column._get_value(product)))
        return [self.text_separator.join('"%s"' % value for value in values)]

    def _add_warning(self, message: str) -> None:
        self.ensure_one()
        if not self.warning_messages:
            self.warning_messages = f"{message}"
        else:
            self.warning_messages = f"{self.warning_messages}\n{message}"

    def _post_warnings(self) -> None:
        self.ensure_one()
        messages = set(self.warning_messages.split('\n') if self.warning_messages else [])
        warning_list = _(
            "<p class='font-weight-bold text-warning'>Warnings:</p><ul>%s</ul>",
            "".join(["<li>%s</li>" % warn for warn in messages]),
        ) if messages else ''
        html_message = Markup(_("<p>The feed is generated.</p>%s", warning_list))
        if not self.env.context.get('without_headers', False):
            self.message_post(body=html_message)
        # Clean warnings
        self.warning_messages = ''

    def generate_data_file(self) -> str:
        self.ensure_one()
        feed = self
        # Clear a feed and column warnings
        feed.column_ids.write({'feed_warning': None})
        feed.warning_messages = ''

        if feed.file_type == 'xml':
            return feed.generate_data_file_xml()
        if feed.file_type not in ['csv', 'tsv']:
            return ''

        rows = []
        separator = feed.text_separator or feed.file_type == 'tsv' and '\t' or ','
        without_headers = self.env.context.get('without_headers', False)

        # Add file header
        if not without_headers:
            columns = feed.column_ids.mapped('name')
            rows.append(separator.join('"%s"' % name for name in columns))

        # Generate file rows
        for product in feed.get_items_with_context():
            rows += feed._get_text_lines(product)

        feed._post_warnings()
        return '\n'.join(rows)

    def generate_data_file_xml(self):
        """ Generate data feed XML file. Method declaration to inherit."""
        self.ensure_one()
        # Clear column warnings
        self.column_ids.write({'feed_warning': None})
        self.warning_messages = ''
        self._post_warnings()
        return ''

    def action_generate_token(self):
        self.ensure_one()
        self.access_token = self._generate_access_token()

    def action_record_list(self):
        self.ensure_one()
        return {
            'name': _('Feed Items'),
            'type': 'ir.actions.act_window',
            'res_model': self._get_source_feed().model_name,
            'view_mode': 'list,form',
            'domain': self._get_source_feed().model_domain,
        }

    def action_download(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '%s' % (self.url if not self.env.context.get('preview_mode')
                # Add extra query parameter "preview_mode" to feed URL to avoid feed compression
                else f"{self.url}{'?' if not self.use_token else '&'}preview_mode=True"),
            'target': 'new',
        }

    def action_preview_csv(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/product_data/preview_csv/{self.id}',
            'target': 'new',
        }

    def copy(self, default=None):
        new_feeds = super(ProductDataFeed, self).copy(default=default)
        for old_feed, new_feed in zip(self, new_feeds):
            # Copy feed columns
            for column in old_feed.with_context(active_test=False).column_ids:
                column.copy(default={'feed_id': new_feed.id})
            # Copy child feeds
            child_feeds = self.search([('parent_feed_id', '=', old_feed.id)])
            if child_feeds:
                child_feeds.copy(default={'parent_feed_id': new_feed.id})
        return new_feeds

    def copy_data(self, default=None):
        vals_list = super(ProductDataFeed, self).copy_data(default=default)
        for feed, vals in zip(self, vals_list):
            vals['name'] = _("%s (copy)", feed.name)
            if vals.get('access_token'):
                vals['access_token'] = self._generate_access_token()
            if vals.get('filename'):
                vals['filename'] = self._default_filename()
        return vals_list
