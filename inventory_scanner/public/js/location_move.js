frappe.ui.form.on("Location", {
	refresh(frm) {
		if (frm.is_new()) return;

		frm.add_custom_button(__("Move items"), () => {
			const d = new frappe.ui.Dialog({
				title: __("Move items from {0}", [frm.doc.name]),
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
						fieldname: "to_location",
						label: __("Destination"),
						fieldtype: "Link",
						options: "Location",
						reqd: 1,
					},
				],
				primary_action_label: __("Move"),
				async primary_action(values) {
					const sources = await frappe.db.get_list("Item Placement", {
						filters: { item_code: values.item_code, location: frm.doc.name },
						fields: ["name", "warehouse"],
					});
					if (!sources.length) {
						frappe.msgprint(__("{0} isn't on this shelf.", [values.item_code]));
						return;
					}
					if (sources.length > 1) {
						frappe.msgprint(
							__("{0} is on this shelf for more than one warehouse.", [values.item_code]),
						);
						return;
					}
					const source = sources[0];

					const destinations = await frappe.db.get_list("Item Placement", {
						filters: {
							item_code: values.item_code,
							location: values.to_location,
							warehouse: source.warehouse,
						},
						fields: ["name"],
					});
					if (!destinations.length) {
						frappe.msgprint(
							__("{0} isn't on {1} yet.", [values.item_code, values.to_location]),
						);
						return;
					}

					frappe.call({
						method: "inventory_scanner.moving_items.item_placement_move.move_item_placement",
						args: {
							source_placement: source.name,
							destination_placement: destinations[0].name,
							quantity: values.qty,
						},
						freeze: true,
						freeze_message: __("Moving..."),
						callback(r) {
							if (!r.message) return;
							d.hide();
							frm.reload_doc();
							frappe.show_alert({
								message: __("Moved {0} × {1} to {2}", [
									r.message.moved_quantity,
									r.message.item,
									r.message.to_location,
								]),
								indicator: "green",
							});
						},
					});
				},
			});
			d.show();
		});
	},
});