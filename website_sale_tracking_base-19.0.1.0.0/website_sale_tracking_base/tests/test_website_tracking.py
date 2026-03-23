from odoo.tests import tagged
from odoo.tests.common import HttpCase


@tagged('post_install', '-at_install', 'website_tracking')
class TestWebsiteTracking(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.company.website_id
        cls.website.write({
            'tracking_is_active': True,
            'tracking_is_logged': True,
        })
        cls.test_product_template = cls.env.ref('sale.product_product_1_product_template')
        cls.test_product_variant = cls.test_product_template.product_variant_id
        cls.test_public_category = cls.env.ref('website_sale.public_category_desks')
        cls.tracking_service = cls.env['website.tracking.service'].create([{
            'key': 'TEST-001',
            'is_internal_logged': True,
        }])

    def test_01_event_view_product_list(self):
        self.start_tour('/shop', 'tracking_event_view_product_list_tour')
        tracking_log = self.env['website.tracking.log'].search([
            ('service_id', '=', self.tracking_service.id),
        ])
        self.assertEqual(len(tracking_log), 1, '"View Product List" log should exist.')
        self.assertEqual(tracking_log.event_type, 'view_product_list')
        self.assertNotEqual(tracking_log.product_ids, False)

    def test_02_event_view_product(self):
        self.start_tour(self.test_product_variant.website_url, 'tracking_event_view_product_tour')
        tracking_log = self.env['website.tracking.log'].search([
            ('service_id', '=', self.tracking_service.id),
        ])
        self.assertEqual(len(tracking_log), 1, '"View Product" log should exist.')
        self.assertEqual(tracking_log.event_type, 'view_product')
        self.assertNotEqual(tracking_log.product_id, False)

    def test_03_event_view_product_category(self):
        self.start_tour(f'/shop/category/{self.test_public_category.id}',
        'tracking_event_view_product_category_tour')
        tracking_log = self.env['website.tracking.log'].search([
            ('service_id', '=', self.tracking_service.id),
            ('event_type', '=', 'view_product_category')
        ])
        self.assertEqual(len(tracking_log), 1, '"View Product Category" log should exist.')
        self.assertNotEqual(tracking_log.product_ids, False, 'Products for test category should be logged.')

    def test_04_event_search_product(self):
        search_term = 'desk'
        self.start_tour(f'/shop?&search={search_term}', 'tracking_event_search_product_tour')
        tracking_log = self.env['website.tracking.log'].search([
            ('service_id', '=', self.tracking_service.id),
            ('event_type', '=', 'search_product')
        ])
        self.assertEqual(len(tracking_log), 1, '"Search Product" log should exist.')
        self.assertEqual(tracking_log.search_term, search_term, 'Search term should be logged.')

    def test_05_event_add_to_cart(self):
        self.start_tour('/shop', 'tracking_event_add_to_cart_tour')
        tracking_log = self.env['website.tracking.log'].search([
            ('service_id', '=', self.tracking_service.id),
            ('event_type', '=', 'add_to_cart'),
        ])
        self.assertEqual(len(tracking_log), 2, '"Add to Cart" logs should exist.')
        self.assertEqual(
            tracking_log[0].product_id, self.test_product_variant,
         'Tracked product should match to test product variant.'
        )

    def test_06_event_add_to_wishlist(self):
        if self.env['ir.module.module']._get('website_sale_wishlist').state == 'installed':
            self.start_tour('/shop', 'tracking_event_add_to_wishlist_tour')
            tracking_log = self.env['website.tracking.log'].search([
                ('service_id', '=', self.tracking_service.id),
                ('event_type', '=', 'add_to_wishlist'),
            ])
            self.assertEqual(len(tracking_log), 2, '"Add to Wishlist" logs should exist.')
            self.assertEqual(
                tracking_log[0].product_id, self.test_product_variant,
                'Tracked product should match to test product variant',
            )
        else:
            self.skipTest('Can not test tracking "add_to_wishlist" event because '
                          '"website_sale_wishlist" module is not installed')

    def test_07_event_login(self):
        self.start_tour('/web/login', 'tracking_event_login_tour')
        tracking_log = self.env['website.tracking.log'].search([
            ('service_id', '=', self.tracking_service.id),
        ])
        self.assertEqual(len(tracking_log), 1, '"Login" log should exist.')
        self.assertEqual(tracking_log.event_type, 'login')

    def test_08_cart_action_events(self):
        self.start_tour('/shop', 'tracking_event_cart_actions_tour')
        tracking_log = self.env['website.tracking.log'].search([
            ('service_id', '=', self.tracking_service.id),
            ('event_type', 'in', ['update_cart','remove_from_cart']),
        ])
        self.assertEqual(
            len(tracking_log.filtered(lambda log: log.event_type == 'update_cart')), 1,
            '"Update Cart" event should exist.'
        )
        self.assertEqual(
            len(tracking_log.filtered(lambda log: log.event_type == 'remove_from_cart')), 1,
            '"Remove from Cart" event should exist.'
        )

    def test_09_checkout_process_events(self):
        if self.env['ir.module.module']._get('payment_demo').state != 'installed':
            self.skipTest("Demo payment provider is not installed")
        else:
            self.start_tour('/shop', 'tracking_event_checkout_process_tour')
            tracking_log = self.env['website.tracking.log'].search([
                ('service_id', '=', self.tracking_service.id),
            ])
            self.assertEqual(
                len(tracking_log.filtered(lambda log: log.event_type == 'begin_checkout')), 1,
                '"Begin Checkout" event should exist.'
            )
            self.assertEqual(
                len(tracking_log.filtered(lambda log: log.event_type == 'add_payment_info')), 1,
                '"Add Payment Info" event should exist.'
            )
            self.assertEqual(
                len(tracking_log.filtered(lambda log: log.event_type == 'purchase')), 1,
                '"Purchase" event should exist.'
            )

    def test_10_event_purchase_portal(self):
        if self.env['ir.module.module']._get('payment_demo').state != 'installed':
            self.skipTest("Demo payment provider is not installed")
        else:
            order = self.env.ref('sale.portal_sale_order_1')
            self.start_tour(
                f'/my/orders/{order.id}', 'tracking_event_purchase_portal_tour', login='portal')
            tracking_log = self.env['website.tracking.log'].search([
                ('service_id', '=', self.tracking_service.id),
                ('event_type', '=', 'purchase_portal')
            ])
            self.assertEqual(len(tracking_log), 1, '"Purchase Portal" event should exist.')

    def test_11_event_signup(self):
        self.start_tour('/web/signup', 'tracking_event_sign_up_tour')
        tracking_log = self.env['website.tracking.log'].search([
            ('service_id', '=', self.tracking_service.id),
        ])
        self.assertEqual(len(tracking_log), 1, '"Sign Up" log should exist.')
        self.assertEqual(tracking_log.event_type, 'sign_up')

    def test_12_event_lead(self):
        if self.env['ir.module.module']._get('website_crm').state != 'installed':
            self.skipTest('"website_crm" module is not installed. Skip test lead event.)')
        else:
            # Change default contactus form to lead form
            self.start_tour(
                self.env['website'].get_client_action_url('/contactus'),
                'website_crm_pre_tour',
                login='admin'
            )
            # Send form
            self.start_tour('/contactus', 'website_crm_tour')
            tracking_log = self.env['website.tracking.log'].search([
                ('service_id', '=', self.tracking_service.id),
            ])
            self.assertEqual(len(tracking_log), 1, '"Lead" log should exist.')
            self.assertEqual(tracking_log.event_type, 'lead')
