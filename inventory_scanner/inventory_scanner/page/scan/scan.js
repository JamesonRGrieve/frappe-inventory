// One big button on Scan page that opens the scanner
// A worker can scan a sticker from anywhere in the app
// without first opening a list.  Scanner live in shared
// helper (public/js/scan_helper.js), which hooks.py on
// every desk page.
frappe.pages["scan"].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Scan"),
        single_column: true,
    });

    const $body = $(`
        <div class="text-center" style="padding: 48px 16px;">
            <p class="text-muted">
                ${__("Scan a Warehouse, Location, Item or Asset sticker to open its record.")}
            </p>
            <button class="btn btn-primary btn-lg scan-start">${__("Scan")}</button>
        </div>
    `).appendTo(page.main);

    $body.find(".scan-start").on("click", () => inventory_scanner.scan_and_open());
};