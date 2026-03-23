import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("tracking_event_login_tour", {
    steps: () => [
        {
            content: 'Fill "login" input.',
            trigger: 'input[name="login"]',
            run: 'edit portal',
        },
        {
            content: 'Fill "password" input',
            trigger: 'input[name="password"]',
            run: 'edit portal',
        },
        {
            content: 'Click "Log in" button (for register "login" event).',
            trigger: 'button[type="submit"]',
            run: 'click',
            expectUnloadPage: true,
        }
    ]
});
