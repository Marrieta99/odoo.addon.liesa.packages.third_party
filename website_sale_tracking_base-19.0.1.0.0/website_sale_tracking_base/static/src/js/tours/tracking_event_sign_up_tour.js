import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("tracking_event_sign_up_tour", {
    steps: () => [
        {
            content: 'Fill "Name" input',
            trigger: '#name',
            run: 'edit TestUser',
        },
        {
            content: 'Fill "Login" input',
            trigger: '#login',
            run: 'edit test-user',
        },
        {
            content: 'Fill "Password" input',
            trigger: '#password',
            run: "edit cdfv1234qwerty",
        },
        {
            content: 'Fill "Confirm Password" input',
            trigger: '#confirm_password',
            run: "edit cdfv1234qwerty",
        },
        {
            content: 'Submit form (for register "sign_up" event).',
            trigger: '.oe_signup_form button.btn-primary',
            run: 'click',
            expectUnloadPage: true,
        }
    ]
});
