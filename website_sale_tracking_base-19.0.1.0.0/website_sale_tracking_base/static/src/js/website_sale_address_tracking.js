import { CustomerAddress } from '@portal/interactions/address';
import { patch } from '@web/core/utils/patch';
import { trackingExecuteEvent } from '@website_sale_tracking_base/js/utils';

patch(CustomerAddress.prototype, {
    async saveAddress(ev) {
        ev.preventDefault();
        let eventBtn = ev.currentTarget;
        // if customer fills address in checkout process (not from portal settings)
        if (eventBtn.getAttribute('name') == 'website_sale_main_button') {
            await trackingExecuteEvent({
                event_type: 'add_shipping_info',
            }, 'Add Shipping Info');
        }
        return super.saveAddress(ev);
    }
});
