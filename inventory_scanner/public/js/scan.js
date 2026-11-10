// Adds a Scan button to the Warehouse, Item and Asset lists
// and to the Warehouse tree.  They all do the same thing,
// which is open the scanner.  The scanning itself lives
// in scan_helper.js (inventory_scanner.scan_and_open).
(() => {
	frappe.listview_settings["Warehouse"] = {
		onload(listview) {
			listview.page.add_inner_button(__("Scan Warehouse"), () => {
				inventory_scanner.scan_and_open();
			});
		},
	};

	frappe.listview_settings["Item"] = {
		onload(listview) {
			listview.page.add_inner_button(__("Scan Item"), () => {
				inventory_scanner.scan_and_open();
			});
		},
	};

	frappe.listview_settings["Asset"] = {
		onload(listview) {
			listview.page.add_inner_button(__("Scan Asset"), () => {
				inventory_scanner.scan_and_open();
			});
		},
	};

	// Warehouse opens on its tree view by default, so it needs a button
	// there too.  We wrap the existing onload (ERPNext may have its own)
	// and set scan_button_added so the button isn't added twice if
	// this runs again.
	const tree = frappe.treeview_settings["Warehouse"];
	if (tree && !tree.scan_button_added) {
		const original_onload = tree.onload;
		tree.onload = (treeview) => {
			if (original_onload) original_onload(treeview);
			const $btn = treeview.page.add_inner_button(__("Scan Warehouse"), () => {
				inventory_scanner.scan_and_open();
			});
			// Only move the button if add_inner_button returned it (version dependent)
			if ($btn && $btn.length) $btn.parent().prepend($btn);
		};
		tree.scan_button_added = true;
	}
})();