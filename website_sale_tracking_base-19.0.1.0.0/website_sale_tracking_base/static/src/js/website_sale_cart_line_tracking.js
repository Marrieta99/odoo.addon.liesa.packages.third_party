import { CartLine } from '@website_sale/interactions/cart_line';
import { patch } from '@web/core/utils/patch';
import { trackingExecuteEvent, debouncedTrackingEvent } from '@website_sale_tracking_base/js/utils';

patch(CartLine.prototype, {

    /**
     * Override
     * @param {Event} ev
     * @param {HTMLElement} currentTargetEl
     */
     async _changeQuantity(input) {
        let quantity = parseInt(input.value || 0);
        if (isNaN(quantity)) { quantity = 1 };
        if (quantity) {
            debouncedTrackingEvent({
                event_type: 'update_cart',
                item_type: 'product.product',
                product_ids: [parseInt(input.dataset.productId),],
                product_qty: quantity,
            }, 'Update Cart');
        } else {
            // In this case window.location can be changed from promise resolve inside super method
            // to avoid situations when the tracked data does not have time to be sent,
            // we need to wait for it to be sent
            await this.waitFor(
                trackingExecuteEvent({
                    event_type: 'remove_from_cart',
                    item_type: 'product.product',
                    product_ids: [parseInt(input.dataset.productId),],
                    product_qty: 0,
                }, 'Remove From Cart')
            );
        }
        return super._changeQuantity(input);
     }

});
