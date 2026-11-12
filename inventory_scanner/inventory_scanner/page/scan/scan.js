// Scan page.  Worker picks what a scan should do and
// keeps scanning.  "Open record" is the one scan 
// behavior from the list buttons.  Any other action
// keeps the camera opena and applies the action to
// every label scanned.
frappe.pages["scan"].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Scan"),
        single_column: true,
    });

    const actions = {
        checkout: {
            label: __("Check Out"),
            doctype: "Asset",
            run: (asset_id) =>
                frappe.call({
                    method: "inventory_scanner.moving_items.asset_checkout.checkout_asset",
                    args: { asset_id },
                    silent: true, // no erro dialog
                }),
        },
        checkin: {
            label: __("Check In"),
            doctype: "Asset",
            needs_shelf: true, // worker picks a shelf before scanning
            run: (asset_id, shelf) =>
                frappe.call({
                    method: "inventory_scanner.moving_items.asset_checkin.checkin_asset",
                    args: { asset_id, location: shelf },
                    silent: true,
                }),
        }
    };

    const open_label = __("Open record");
    const labels = [open_label, ...Object.values(actions).map((a) => a.label)];
    const action_field = page.add_field({
        fieldname: "action",
        label: __("Action"),
        fieldtype: "Select",
        options: labels.join("\n"),
        default: open_label,
    });

    const shelf_field = page.add_field({
        fieldname: "shelf",
        label: __("Shelf (for Check in)"),
        fieldtype: "Link",
        options: "Location",
        change: () => show_shelf(shelf_field.get_value()),
    });


    const $body = $(`
        <div style="padding: 24px 16px; max-width: 640px; margin: 0 auto; text-align: center;">
            <p class="text-muted">${__("Pick an action, then scan labels. Camera stays open until you close it")}</p>
            <div style="display: flex; gap: 8px; flex-wrap: wrap; justify-content: center;">
                <button class="btn btn-default btn-lg scan-shelf">${__("Scan Shelf")}</button>
                <button class="btn btn-primary btn-lg scan-start">${__("Scan")}</button>
            </div>
            <p class="shelf-chosen text-muted" style="margin-top: 12px;"></p>
            <ul class="scan-results list-unstyled" style="margin-top: 24px; text-align: left;"></ul>
        </div>
    `).appendTo(page.main);
    const $results = $body.find(".scan-results");

    //Shows the chosen shelf next to the button, so a worker
    // can see where the check ins will go without looking 
    // up at the shelf too
    const show_shelf = (name) => 
        $body.find(".shelf-chosen").text(name ? __("Shelf: {0}", [name]) : "");

    // scan a shelf sticker to fill the Shelf box instead of picking from a long list
    $body.find(".scan-shelf").on("click", () => {
        inventory_scanner.scan_for("Location", (name) => {
            shelf_field.set_value(name);
            show_shelf(name);
        });
    });

    // Shelf controls only matter for actions that need a shelf (check in)
    const update_for_action = () => {
        const action = Object.values(actions).find((a) => a.label === action_field.get_value());
        const needs_shelf = Boolean(action && action.needs_shelf);
        $body.find(".scan-shelf").toggle(needs_shelf);
        $body.find(".shelf-chose").toggle(needs_shelf);
        shelf_field.$wrapper.toggle(needs_shelf);
    };

    action_field.$input.on("change", update_for_action);
    update_for_action(); // sets the right starting state

    
    // 1 scan per scan, pop up while camera is up and a list is on the page.
    const add_line = (text, ok) => {
        frappe.show_alert({ message: text, indicator: ok ? "green" : "red"}, 4);
        $(`<li>${ok ? "✓" : "✗"} ${frappe.utils.escape_html(text)}</li>`).prependTo($results);
    };

    // failed call comes back with server's message
    const reason = (err) => {
        try {
            const raw = err._server_messages || (err.responseJSON && err.responseJSON._server_messages);
            if (raw) return $("<div>").html(JSON.parse(JSON.parse(raw)[0]).message).text();
        } catch (e) {
        // allow regular message
    }
    return __("Something went wrong.");
};

    const handle_scan = async (text, action, shelf) => {
        let url;
        try {
            url = new URL(text);
        } catch (e) {
            add_line(__("Scanned text is not a valid link"), false);
            return;
        }
        if (url.origin !== window.location.origin) {
            add_line(__("QR code isn't from this site: {0}", [text]), false);
            return;
        }
        // link ends in /<doctype-slug>/<record name>
        const parts = url.pathname.split("/").filter(Boolean).map(decodeURIComponent);
        const name = parts[parts.length -1];
        const slug = parts[parts.length -2];
        if (slug !== action.doctype.toLowerCase().replace(/ /g, "-")) {
            add_line(__("{0} is not a {1}", [name, action.doctype]), false);
            return;
        }
        try{
            const r = await action.run(name, shelf);
            add_line(`${name}: ${r.message.message}`, true);
        } catch (err) {
            add_line(`${name}: ${reason(err)}`, false);
        }
    };

    $body.find(".scan-start").on("click", () => {
        const chosen = action_field.get_value();
        if (chosen === open_label) {
            inventory_scanner.scan_and_open();
            return;
        }
        const action = Object.values(actions).find((a) => a.label === chosen);

        // Check in needs a shelf to put asset on, asks before camera opens
        const shelf = shelf_field.get_value();
        if (action.needs_shelf && !shelf) {
            frappe.msgprint(__("Pick a shelf first, so each check in knows where to put the asset"));
            return;
        }

        // scanner reports every camera frame in multiple mode,
        // skip a code we saw a momemnt ago (label is still in view).
        let last_code = null;
        let last_seen = 0;
        new frappe.ui.Scanner({
            dialog: true,
            multiple: true,
            on_scan(data) {
                const now = Date.now();
                const repeat = data.decodedText == last_code && now - last_seen < 3000;
                last_code = data.decodedText;
                last_seen = now;
                if (!repeat) handle_scan(data.decodedText, action, shelf);
            },
        });
    });
};