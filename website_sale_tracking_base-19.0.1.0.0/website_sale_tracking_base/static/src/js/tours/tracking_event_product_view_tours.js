import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("tracking_event_view_product_list_tour", {
    url: '/shop',
    steps: () => [
        {
            content: 'Open website shop page (for register "view_product_list" event).',
            trigger: 'body',
            run: () => {
                const trackLogAttr = document.body.getAttribute('data-log-tracking-events');
                if (!trackLogAttr) {
                    console.error("Body element should has 'data-log-tracking-events' attribute!");
                }
            }
        }
    ]
});

registry.category("web_tour.tours").add("tracking_event_view_product_tour", {
    steps: () => [
        {
            content: 'Open product page on website (for register "view_product" event).',
            trigger: '#product_detail',
            run: () => {
                let altProductInput = $('input[name="alt_product_id"]');
                let altProductTemplateInput = $('input[name="alt_product_template_id"]');
                if (!altProductInput.length) {
                    console.error('Custom added hidden input (product_id) should exist!');
                }
                if (!altProductTemplateInput.length) {
                    console.error('Custom added hidden input (product_template_id) should exist!');
                }
            }
        }
    ]
});

registry.category("web_tour.tours").add("tracking_event_view_product_category_tour", {
    steps: () => [
        {
            content: 'Open website shop page with selected product category (for register "view_product_category" event).',
            trigger: '#products_grid',
            run: () => {
                let productCategoryAttr = $('#products_grid').data('tracking_category');
                if (!productCategoryAttr) {
                    console.error("Products grid element should has 'data-tracking_category' attribute!");
                }
            }
        }
    ]
});

registry.category("web_tour.tours").add("tracking_event_search_product_tour", {
    steps: () => [
        {
            content: 'Open website shop page with specified search term (for register "search_product" event).',
            trigger: '#products_grid',
            run: () => {
                let searchTermAttr = $('#products_grid').data('tracking_search_term');
                if (!searchTermAttr) {
                    console.error("Products grid element should has 'data-tracking_search_term' attribute!");
                }
            }
        }
    ]
});
