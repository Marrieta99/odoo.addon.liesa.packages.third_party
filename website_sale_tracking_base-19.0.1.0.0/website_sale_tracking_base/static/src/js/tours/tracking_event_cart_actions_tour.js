import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("tracking_event_cart_actions_tour", {
    steps: () => [
        {
            content: 'Add product to cart from product list.',
            trigger: 'form:has(span:contains(Chair floor protection)) button.a-submit:not(:visible)',
            run: async() => {
                let $addToCartBtn = $('form:has(span:contains(Chair floor protection)) button.a-submit')
                $addToCartBtn.click();
                // Wait for cart update
                await new Promise(resolve => setTimeout(resolve, 1000));
            },
        },
        {
            content: 'Go to cart page.',
            trigger: 'a[href="/shop/cart"]',
            run: 'click',
            expectUnloadPage: true
        },
        // UPDATE CART
        {
            content: "add one more",
            trigger: '#cart_products div:has(a[name="o_cart_line_product_link"]>h6:contains("Chair floor protection")) a:has(i.oi-plus)',
            run: "click",
        },
        // REMOVE FROM CART EVENT
        {
            content: 'Click "Remove" to remove product from cart (for register "remove_cart" event).',
            trigger: '#shop_cart',
            run: async () => {
                await new Promise(resolve => setTimeout(resolve, 3000));
                let $removeCartBtn = $('.js_delete_product');
                $removeCartBtn.trigger('click');
            },
            expectUnloadPage: true
        },
    ]
});
