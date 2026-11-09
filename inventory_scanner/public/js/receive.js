frappe.ui.form.on("Item", {
  refresh(frm) {
    if (frm.is_new()) return;

    frm.add_custom_button(__("Receive"), () => {
      // Defaults for this company, falling back to the first Item Defaults row
      const company = frappe.defaults.get_user_default("Company");
      const defaults =
        (frm.doc.item_defaults || []).find((d) => d.company === company) ||
        (frm.doc.item_defaults || [])[0] ||
        {};
      const warehouse = defaults.default_warehouse;
      const supplier =
        defaults.default_supplier ||
        ((frm.doc.supplier_items || [])[0] || {}).supplier;

      frappe.model.with_doctype("Purchase Receipt", () => {
        const pr = frappe.model.get_new_doc("Purchase Receipt");
        const row = frappe.model.add_child(pr, "items");
        row.qty = 1;
        row.received_qty = 1;

        frappe.set_route("Form", "Purchase Receipt", pr.name).then(() => {
          setTimeout(() => {
            const pr_frm = cur_frm;
            if (pr_frm && pr_frm.doc.doctype === "Purchase Receipt") {
              // Item code
              frappe.model.set_value(row.doctype, row.name, "item_code", frm.doc.name);

              // Warehouse from Item Defaults
              if (warehouse) {
                frappe.model.set_value(row.doctype, row.name, "warehouse", warehouse);
                pr_frm.set_value("set_warehouse", warehouse);
              }

              // Supplier from Item Defaults, or the Item Supplier table
              if (supplier) {
                pr_frm.set_value("supplier", supplier);
              }
            }
          }, 300);
        });
      });
    });
  },
});