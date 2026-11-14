// Shared scanning helpers.  This file loads on every desk page
// (app_include_js in hooks.py) so any other script, like the
// scan buttons or the Scan page can call 
// inventory_scanner.scan_and_open() without defining its 
// own scanner.
frappe.provide("inventory_scanner");

// Reads a scanned code and says what it points to. Returns
// { name, slug, url } for a link to a record on this site, 
// or { error } with a message.  If doctype is passed, the
// link must be to that kind of record.  Callers decide 
// what to do next.
inventory_scanner.parse_scan = (text, doctype) => {
    let url;
    try {
        url = new URL(text);
    } catch (e) {
        // Anything that isn't a full URL.
        return { error: __("Scanned text is not a valid link") };
    }
    // Only follow links that point at this site.  Won't allow
    // another QR from somewhere else.
    if (url.origin !== window.location.origin) {
        return { error: __("QR code isn't from this site") };
    }
    // link ends in /<doctype-slug>/<record name>
    let parts;
    try {
        parts = url.pathname.split("/").filter(Boolean).map(decodeURIComponent);
    } catch (e) {
        // stray % in a label makes decodeURIComponent throw
        return { error: __("Scanned link is not valid") };
    }
    const name = parts[parts.length - 1];
    const slug = parts[parts.length - 2];
    if (doctype && slug !== frappe.router.slug(doctype)) {
        return { error: __("Wrong kind of label: {0} (expected {1})", [name || text, doctype]) };
    }
    return { name, slug, url };
};

// Opens the record that a scanned QR code points to. The labels
// hold a full link to the record, so scanning one is the same
// following that link.
inventory_scanner.open_scanned_link = (text) => {
    const scan = inventory_scanner.parse_scan(text);
    if (scan.error) {
        frappe.msgprint(scan.error);
        return;
    }
    window.location.assign(scan.url.href);
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

// Scans one label and hands back the name of the record on it only if
// it is the kind of record asked for (ex: "Location").  Lets a page
// fill in a field by scanning a sticker instead of picking it from a long list.
inventory_scanner.scan_for = (doctype, on_name) => {
    new frappe.ui.Scanner({
        dialog: true,
        multiple: false,
        on_scan(data) {
            const scan = inventory_scanner.parse_scan(data.decodedText, doctype);
            if (scan.error) {
                frappe.msgprint(scan.error);
                return;
            }
            on_name(scan.name);
        },
    });
};

// Add "Scan" button to every desk page for worker to scan a sticker
// from wherever they are without opening a list or the Scan page first.
inventory_scanner.add_scan_button = () => {
    //prevents adding a second button if file runs more than once
    if ($(".inventory-scanner-fab").length) return;

    $(`<button class="btn btn-primary btn-lg inventory-scanner-fab">${__("Scan")}</button>`)
        .css({
            position: "fixed",
            right: "24px",
            bottom: "24px",
            "z-index": 1000,
            "border-radius": "999px",
            "box-shadow": "var(--shadow-lg)",
        })
        .on("click", () => inventory_scanner.scan_and_open()).appendTo("body");
};

// Scan page has its own Scan button, hide floating button here.
inventory_scanner.update_scan_button = () => {
    // route is null until the router has run once (fresh page load) so default
    // to an empty list
    const route = frappe.get_route() || [];
    const on_scan_page = route[0] === "scan";
    $(".inventory-scanner-fab").toggle(!on_scan_page);
};

$(document).ready(() => {
    inventory_scanner.add_scan_button();
    // opens the Scan page directly, before route change fires
    inventory_scanner.update_scan_button();
    frappe.router.on("change", inventory_scanner.update_scan_button);
});