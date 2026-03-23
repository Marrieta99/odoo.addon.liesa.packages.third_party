import { PaymentForm } from '@payment/interactions/payment_form';
import { patch } from '@web/core/utils/patch';
import { trackingExecuteEvent } from '@website_sale_tracking_base/js/utils';

patch(PaymentForm.prototype, {

    async submitForm(ev) {
        ev.stopPropagation();
        ev.preventDefault();
        this._disableButton(true);

        // purchase_portal event
        if (document.querySelector('.o_portal_sidebar')) {
            await trackingExecuteEvent({
                event_type: 'purchase_portal',
                order_id: parseInt(this.el.dataset.orderId) || null,
            }, 'Purchase Portal');
        }

        // add_payment_info Event
        const checkedRadio = document.querySelector('input[name="o_payment_radio"]:checked');
        await trackingExecuteEvent({
            event_type: 'add_payment_info',
            payment_provider_id: parseInt(checkedRadio.dataset.providerId, 10),
        }, 'Add Payment Info')

        return super.submitForm(ev);
    }

});
