/** @odoo-module **/
import { Tracking } from '@website_sale/interactions/tracking';
import { registry } from '@web/core/registry';

export class DisableNativeTracking extends Tracking {
    /**
     * Skip Odoo native GA tracking.
     * @override
     */
    _trackGa() {}
}

registry
    .category('public.interactions')
    .add('website_sale.tracking', DisableNativeTracking, {force: true});
