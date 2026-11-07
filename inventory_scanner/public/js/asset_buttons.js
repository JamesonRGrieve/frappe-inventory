function scan_shelf_into(dialog) {
    new frappe.ui.Scanner({
        dialog: true,
        multiple: false,
        on_scan(data) {
            let text = data.decodedText || "";
            if (text.startsWith("http://") || text.startsWith("https://")) {
                text = text.split("/").pop();
            }
            dialog.set_value("location", decodeURIComponent(text));
        },
    });
}

function ask_shelf_and_check_in(frm) {
    const dialog = new frappe.ui.Dialog({
        title: __("Check in {0}", [frm.doc.name]),
        no_focus: true,
        fields: [
            {
                fieldname: "scan_shelf",
                fieldtype: "Button",
                label: __("Scan Shelf"),
                click: () => scan_shelf_into(dialog),
            },
            {
                fieldname: "location",
                fieldtype: "Link",
                options: "Location",
                label: __("Shelf"),
                reqd: 1,
            },
        ],
        primary_action_label: __("Check In"),
        primary_action(values) {
            frappe
                .call({
                    method: "inventory_scanner.moving_items.asset_checkin.checkin_asset",
                    args: { asset_id: frm.doc.name, location: values.location },
                    freeze: true,
                })
                .then ((r) => {
                    dialog.hide();
                    frappe.show_alert({message: r.message.message, indicator: "green"});
                    frm.reload_doc();
                });
        },
    });
    dialog.show();
}

frappe.ui.form.on("Asset", {
	refresh(frm) {
		if (frm.is_new() || frm.doc.docstatus !== 1) return;

		if (!frm.doc.custodian) {
            frm.add_custom_button(__("Check Out"), () => {
                frappe
                    .call({
                        method: "inventory_scanner.moving_items.asset_checkout.checkout_asset",
                        args: { asset_id: frm.doc.name },
                        freeze: true, 
                    })
                    .then((r) => {
                        frappe.show_alert({ message: r.message.message, indicator: "green" });
                        frm.reload_doc();
                    });
            });

        } else {
            frm.add_custom_button(__("Check In"), () => {
                ask_shelf_and_check_in(frm);
            });
        }
	},
});