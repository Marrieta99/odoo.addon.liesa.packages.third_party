# Copyright © 2023 Garazd Creation (https://garazd.biz)
# @author: Yurii Razumovskyi (support@garazd.biz)
# @author: Iryna Razumovska (support@garazd.biz)
# License OPL-1 (https://www.odoo.com/documentation/19.0/legal/licenses.html).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    gtm_container_key = fields.Char(related='website_id.gtm_container_key', readonly=False)

    @api.depends('website_id')
    def _compute_has_google_tag_manager(self):
        for config in self:
            config.has_google_tag_manager = bool(config.gtm_container_key)

    def _inverse_has_google_tag_manager(self):
        for config in self:
            if config.has_google_tag_manager:
                continue
            config.gtm_container_key = False

    has_google_tag_manager = fields.Boolean(
        string='Google Tag Manager',
        compute="_compute_has_google_tag_manager",
        inverse="_inverse_has_google_tag_manager",
    )
