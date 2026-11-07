function ask_shelf_and_check_in(frm) {
    let target = "";
    try {
        target = sessionStorage.getItem("inventory_scanner_checkin_target") || "";
    } catch (e) {}

    const dialog = new frappe.ui.Dialog({
        title:__("Check in {0}", [frm.doc.name]),
        fields: [
            {
                fieldname: "location",
                fieldtype: "Link",
                options: "Location",
                label: __("Shelf"),
                reqd: 1,
                default: target, 
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
                .then((r) => {
                    try {
                        sessionStorage.removeItem("inventory_scanner_checkin_target");
                    } catch (e) {}
                    dialog.hide();
                    frappe.show_alert({ message: r.message.message, indicator: "green" });
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