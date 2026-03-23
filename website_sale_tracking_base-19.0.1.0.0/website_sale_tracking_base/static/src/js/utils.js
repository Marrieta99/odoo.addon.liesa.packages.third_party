/** @odoo-module **/
import { debounce } from "@web/core/utils/timing";
import WebsiteSaleTrackingAlternative from "@website_sale_tracking_base/js/website_sale_tracking";

export async function trackingExecuteEvent(params, message, sync=false) {
    let websiteSaleTracking = new WebsiteSaleTrackingAlternative(this);
    if (websiteSaleTracking.trackingIsLogged()) {
        console.log(websiteSaleTracking.trackingLogPrefix + message);
    }
    if (sync) {
        await websiteSaleTracking.trackingExecuteEventSync(params);
    } else {
        await websiteSaleTracking.trackingExecuteEvent(params);
    }
}

export const debouncedTrackingEvent = debounce(trackingExecuteEvent, 400)
