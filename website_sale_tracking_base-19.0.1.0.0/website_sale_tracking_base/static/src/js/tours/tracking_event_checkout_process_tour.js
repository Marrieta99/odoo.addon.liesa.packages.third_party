import { registry } from "@web/core/registry";
import * as tourUtils from "@website_sale/js/tours/tour_utils";

registry.category("web_tour.tours").add("tracking_event_checkout_process_tour", {
    steps: () => [
        ...tourUtils.searchProduct("Chair floor protection", { select: true }),
        {
            content: "click on add to cart",
            trigger: '#product_detail form #add_to_cart',
            run: "click",
        },
        // Checkout
        tourUtils.goToCart(),
        tourUtils.goToCheckout(),
        ...tourUtils.fillAdressForm({
            name: "John Doe",
            phone: "+380970000001",
            email: "test@example.com",
            street: "Test street, 27",
            city: "Paris",
            zip: "75000",
        }, true),
        {
            content: "Continue checkout",
            trigger: "a[name='website_sale_main_button']",
            run: "click",
            expectUnloadPage: true,
        },
        // Payment
        {
            content: 'eCommerce: select Test payment provider',
            trigger: 'input[name="o_payment_radio"][data-payment-method-code="demo"]',
            run: "click",
        },
        {
            content: 'eCommerce: add card number',
            trigger: 'input[name="customer_input"]',
            run: "edit 4242424242424242",
        },
        ...tourUtils.pay({expectUnloadPage:true, waitFinalizeYourPayment: false}),
        {
            content: 'Wait for transaction polling (redirect after success callback)',
            trigger: 'body',
            expectUnloadPage: true,
        },
        {
            content: 'eCommerce: check that the payment is successful',
            trigger: '[name="order_confirmation"]:contains("Your payment has been processed.")',
        }
    ]
});
