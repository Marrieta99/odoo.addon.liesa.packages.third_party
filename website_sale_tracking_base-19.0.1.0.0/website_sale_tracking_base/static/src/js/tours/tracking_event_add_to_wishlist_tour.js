import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("tracking_event_add_to_wishlist_tour", {
    url: '/shop',
    steps: () => [
        // CASE 1: add product to wishlist from product list
        {
            content: 'Add product to wishlist from product list (for register "add_to_wishlist" event).',
            trigger: 'form:has(span:contains(Customizable Desk)) button.o_add_wishlist',
            run: 'click'
        },
        // CASE 2: add product to wishlist from product page
        {
            content: 'Open product page',
            trigger: 'span:contains(Chair floor protection)',
            run: 'click',
            expectUnloadPage: true
        },
        {
            content: 'Add product to wishlist from product page (for register "add_to_wishlist" event)',
            trigger: 'a.o_add_wishlist_dyn',
            run: 'click'
        }
    ]
});
