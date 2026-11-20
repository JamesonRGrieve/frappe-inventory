// Adds "Print Label Sheet" action to the Item, Asset, Location, and Warehouse list views.
// Loads after scan.js and ERPNext's own list scripts, so it wraps the existing onload
// instead of replacing it.
(function () {
	const DOCTYPES = ["Item", "Asset", "Location", "Warehouse"];
	const CELLS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"];

	DOCTYPES.forEach((doctype) => {
		const settings = (frappe.listview_settings[doctype] =
			frappe.listview_settings[doctype] || {});
		// file loads once per list view, won't wrap same doctype twice
		if (settings.__label_sheet_added) return;
		settings.__label_sheet_added = true;

		const previous_onload = settings.onload;
		settings.onload = function (listview) {
			if (previous_onload) previous_onload.call(this, listview);

			listview.page.add_action_item(__("Print Label Sheet"), () => {
				const names = listview.get_checked_items(true);
				if (!names.length) {
					frappe.msgprint(__("Select at least one record first."));
					return;
				}

				const dialog = new frappe.ui.Dialog({
					title: __("Print Label Sheet"),
					fields: [
						{
							fieldname: "start_cell",
							fieldtype: "Select",
							label: __("Start at cell"),
							options: CELLS,
							default: "1",
							reqd: 1,
							description: __(
								"Cells are numbered left to rightm then down.  1 is top left, 10 is bottom right."
							),
						},
					],
					primary_action_label: __("Open sheet"),
					primary_action(values) {
						// Open a tab first, while the click is still fresh or browser blocks it as popup
						const sheet_window = window.open("", "_blank");
						if (!sheet_window) {
							frappe.msgprint(
								__(
									"Your browser blocked the new tab.  Allow popups for this site and try again."
								)
							);
							return;
						}
						frappe.call({
							method: "inventory_scanner.label_sheet.get_label_sheet_html",
							args: {
								doctype: listview.doctype,
								names: names,
								start_cell: values.start_cell,
							},
							callback(r) {
								sheet_window.document.open();
								sheet_window.document.write(r.message);
								sheet_window.document.close();
								dialog.hid();
							},
							error() {
								sheet_window.close();
							},
						});
					},
				});
				dialog.show();
			});
		};
	});
})();
