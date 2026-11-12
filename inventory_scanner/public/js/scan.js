// Adds a Scan button to the Warehouse, Item and Asset lists
// and to the Warehouse and Location tree.  All buttons will
// open the scanner.
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

	frappe.listview_settings["Location"] = {
		onload(listview) {
			listview.page.add_inner_button(__("Scan Location"), () => {
				inventory_scanner.scan_and_open();
			});
		},
	};

	// Warehouse and Location open on tree view by default, so it needs a button
	// there too.  We wrap the existing onload (ERPNext may have its own)
	// and set scan_button_added so the button isn't added twice if
	// this runs again.
	const tree_labels = {
		Warehouse: __("Scan Warehouse"),
		Location: __("Scan Location"),
	};

	for (const [doctype, label] of Object.entries(tree_labels)) {
		const tree = frappe.treeview_settings[doctype];
		if (tree && !tree.scan_button_added) {
			const original_onload = tree.onload;
			tree.onload = (treeview) => {
				if (original_onload) original_onload(treeview);
				const $btn = treeview.page.add_inner_button(label, () => {
					inventory_scanner.scan_and_open();
				});
				// only move the button if add_inner_button returned it
				if ($btn && $btn.length) $btn.parent().prepend($btn);
			};
			tree.scan_button_added = true;
		}
	}
})();