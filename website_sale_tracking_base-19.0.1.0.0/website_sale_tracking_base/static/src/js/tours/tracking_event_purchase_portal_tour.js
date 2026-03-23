import { registry } from "@web/core/registry";
import { waitUntil, waitFor } from "@odoo/hoot-dom";

registry.category("web_tour.tours").add("tracking_event_purchase_portal_tour", {
    steps: () => [
        {
            content: 'Click "Sign & Pay" button',
            trigger: '#sale_order_sidebar_button a[data-bs-target="#modalaccept"]',
            run: 'click',
        },
        {
            content: 'Wait for modal accept form become visible',
            trigger: '#modalaccept',
            run: async() => {
                await waitFor('#modalaccept:visible', { timeout: 5000 });
            },
        },
        {
            content: "check submit is enabled",
            trigger: '.o_portal_sign_submit:enabled',
        },
        {
            trigger: ".modal .o_web_sign_name_and_signature input:value(Joel Willis)"
        },
        {
            trigger: ".modal canvas.o_web_sign_signature",
            async run(helpers) {
                await waitUntil(() => {
                    const canvas = helpers.anchor;
                    const context = canvas.getContext("2d");
                    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
                    const pixels = new Uint32Array(imageData.data.buffer);
                    return pixels.some((pixel) => pixel !== 0);
                });
            },
        },
        {
            content: "click select style",
            trigger: '.modal .o_web_sign_auto_select_style button',
            run: "click",
        },
        {
            content: "click style 4",
            trigger: ".o-dropdown-item:eq(3)",
            run: "click",
        },
        {
            content: "click submit",
            trigger: '.modal .o_portal_sign_submit:enabled',
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: 'Wait for payment demo modal form become visible',
            trigger: '.modal button[name="o_payment_submit_button"]',
        },
        {
            content: 'Click "Pay" button',
            trigger: 'button[name="o_payment_submit_button"]',
            run: 'click',
            expectUnloadPage: true,
        },
        {
            content: 'Wait for transaction polling (redirect after success callback)',
            trigger: 'body',
            expectUnloadPage: true,
        },
        {
            content: 'eCommerce: check that the payment is successful',
            trigger: '[name="o_payment_status_alert"]:contains("Your payment has been processed.")',
        }
    ]
});
