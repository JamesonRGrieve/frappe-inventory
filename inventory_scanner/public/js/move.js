frappe.ui.form.on("Warehouse", {
	refresh(frm) {
		if (frm.is_new()) return;
		if (frm.doc.is_group) return;

		frm.add_custom_button(__("Move items out"), () => {
			const d = new frappe.ui.Dialog({
				title: __("Move items out of {0}", [frm.doc.name]),
				fields: [
					{
						fieldname: "item_code",
						label: __("Item"),
						fieldtype: "Link",
						options: "Item",
						reqd: 1,
					},
					{
						fieldname: "qty",
						label: __("Quantity"),
						fieldtype: "Float",
						default: 1,
						reqd: 1,
					},
					{
						fieldname: "to_warehouse",
						label: __("Destination"),
						fieldtype: "Link",
						options: "Warehouse",
						reqd: 1,
						get_query: () => ({ filters: { is_group: 0 } }),
					},
				],
				primary_action_label: __("Move"),
				primary_action(values) {
					frappe.call({
						method: "inventory_scanner.moving_items.move_items_out.move_items_out",
						args: {
							from_warehouse: frm.doc.name,
							item_code: values.item_code,
							to_warehouse: values.to_warehouse,
							qty: values.qty,
						},
						freeze: true,
						freeze_message: __("Moving..."),
						callback(r) {
							if (!r.message) return;
							d.hide();
							frappe.show_alert({
								message: __("Moved {0} × {1} to {2}", [
									values.qty,
									values.item_code,
									values.to_warehouse,
								]),
								indicator: "green",
							});
						},
					});
				},
			});
			d.show();
		});

		frm.add_custom_button(__("Move items in"), () => {
			frappe.model.with_doctype("Stock Entry", () => {
				const se = frappe.model.get_new_doc("Stock Entry");
				se.stock_entry_type = "Material Transfer";
				se.to_warehouse = frm.doc.name;
				frappe.set_route("Form", "Stock Entry", se.name);
			});
		});
	},
});