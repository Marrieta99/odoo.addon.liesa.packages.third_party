import { Form } from '@website/snippets/s_website_form/form';
import { patch } from '@web/core/utils/patch';
import { trackingExecuteEvent } from '@website_sale_tracking_base/js/utils';

patch(Form.prototype, {

    /**
     * Override
     * @param {Event} ev
     * @param {HTMLElement} currentTargetEl
     */
    async send(e) {
        // Unlike version 18, we don't need to call e.preventDefault()
        // because the method its prevented using t-on-click.prevent
        // in dynamicContent of Form class
        const _super = super.send.bind(this);
        if (this.checkErrorFields({})) {
            let sync = true;
            let params = { event_type: 'lead' };
            let message = 'Lead (Contact Us - Thank You!)';
            await trackingExecuteEvent(params, message, sync);
            // Additional waiting time for initiating
            // requests intended to send data to tracking services.
            const superWithTimeout = (delay) => new Promise(
                (resolve) => setTimeout(_super, delay, ...arguments)
            );
            return await superWithTimeout(2000);
        }
        return super.send();
    }

});
