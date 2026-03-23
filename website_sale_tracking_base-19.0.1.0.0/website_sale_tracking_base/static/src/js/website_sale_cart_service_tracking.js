import { CartService } from '@website_sale/js/cart_service';
import { patch } from '@web/core/utils/patch';
import { trackingExecuteEvent } from '@website_sale_tracking_base/js/utils';

patch(CartService.prototype, {

    /**
     * @Override
     * Make a request to the server to add the product to the cart.
     */
    async _makeRequest({
        productTemplateId,
        productId,
        quantity,
        uomId=undefined,
        productCustomAttributeValues=[],
        noVariantAttributeValues=[],
        shouldRedirectToCart=false,
        ...rest
    }) {
       let resultQuantity = await super._makeRequest(...arguments);
       // Do the same check as in native tracking Odoo logic
       if ($('body').data('addToCartOnClick') !== 'True' && resultQuantity) {
            await trackingExecuteEvent({
                event_type: 'add_to_cart',
                item_type: 'product.product',
                product_ids: [productId,],
                product_qty: quantity,
            }, 'Add To Cart');
       }
       return resultQuantity
    }

});
