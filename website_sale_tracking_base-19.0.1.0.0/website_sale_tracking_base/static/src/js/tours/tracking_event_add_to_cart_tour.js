import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("tracking_event_add_to_cart_tour", {
    url: '/shop',
    steps: () => [
        // CASE 1: add product to cart from product list
        {
            content: 'Add product to cart from product list (for register "add_to_cart" event).',
            trigger: 'form:has(span:contains(Chair floor protection)) button.a-submit:not(:visible)',
            run: 'click',
        },
         // CASE 2: add product to cart from product page
        {
            content: 'Open product page',
            trigger: 'span:contains(Chair floor protection)',
            run: 'click',
            expectUnloadPage: true
        },
        {
            content: 'Add product to cart from product page (for register "add_to_cart" event)',
            trigger: '#add_to_cart',
            run: 'click'
        }
    ]
});
