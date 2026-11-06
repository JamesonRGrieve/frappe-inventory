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
                frappe
                    .call({
                        method: "inventory_scanner.moving_items.asset_checkin.checkin_asset",
                        args: { asset_id: frm.doc.name },
                        freeze: true,
                    })
                    .then((r) => {
                        frappe.show_alert({ message: r.message.message, indicator: "green" });
                        frm.reload_doc();
                    });
            });
        }
	},
});