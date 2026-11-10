// Shared scanning helpers.  This file loads on every desk page
// (app_include_js in hooks.py) so any other script, like the
// scan buttons or the Scan page can call 
// inventory_scanner.scan_and_open() without defining its 
// own scanner.
frappe.provide("inventory_scanner");

// Opens the record that a scanned QR code points to. The labels
// hold a full link to the record, so scanning one is the same
// following that link.
inventory_scanner.open_scanned_link = (text) => {
    let url;
    try {
        url = new URL(text);
    } catch (e) {
        // Anything that isn't a full URL.
        frappe.msgprint(__("Scanned text is not a valid link"));
        return;
    }
    // Only follow links that point at this site.  This stops a QR
    // from somewhere else, such as a printed sticker from another
    // system, from sending the user away.
    if (url.origin !== window.location.origin) {
        frappe.msgprint(__("QR code isn't from this site"));
        return;
    }
    window.location.assign(url.href);
};

// opens camera scanner and once code is read, opens the record it
// points to.
inventory_scanner.scan_and_open = () => {
    new frappe.ui.Scanner({
        dialog: true,
        multiple: false,
        on_scan(data) {
            inventory_scanner.open_scanned_link(data.decodedText);
        },
    });
};