frappe.ui.form.on("Location", {
    refresh(frm) {
        if(frm.is_new() || frm.doc.is_group) return;
        frm.add_custom_button(__("Check In Here"), () => {
            try {
                sessionStorage.setItem("inventory_scanner_checkin_target", frm.doc.name);
            } catch (e) {}
            frappe.show_alert({
                message:__("Next check in goes to {0}.  Open the asset and tap Check In.", [frm.doc.name]),
                indicator: "green",
            });
        });
    },
});