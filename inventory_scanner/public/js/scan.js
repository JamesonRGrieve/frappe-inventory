(() => {
	const open_scanned_link = (text) => {
		let url;
		try {
			url = new URL(text);
		} catch (e) {
			frappe.msgprint(__("Scanned text is not a valid link."));
			return;
		}
		if (url.origin !== window.location.origin) {
			frappe.msgprint(__("QR code isn't from this site."));
			return;
		}
		window.location.assign(url.href);
	};

	frappe.listview_settings["Warehouse"] = {
		onload(listview) {
			listview.page.add_inner_button(__("Scan Warehouse"), () => {
				new frappe.ui.Scanner({
					dialog: true,
					multiple: false,
					on_scan(data) {
						open_scanned_link(data.decodedText);
					},
				});
			});
		},
	};

	frappe.listview_settings["Item"] = {
		onload(listview) {
			listview.page.add_inner_button(__("Scan Item"), () => {
				new frappe.ui.Scanner({
					dialog: true,
					multiple: false,
					on_scan(data) {
						open_scanned_link(data.decodedText);
					},
				});
			});
		},
	};

	frappe.listview_settings["Asset"] = {
		onload(listview) {
			listview.page.add_inner_button(__("Scan Asset"), () => {
				new frappe.ui.Scanner({
					dialog: true,
					multiple: false,
					on_scan(data) {
						open_scanned_link(data.decodedText);
					},
				});
			});
		},
	};

	const tree = frappe.treeview_settings["Warehouse"];
	if (tree && !tree.scan_button_added) {
		const original_onload = tree.onload;
		tree.onload = (treeview) => {
			if (original_onload) original_onload(treeview);
			treeview.page.add_inner_button(__("Scan Warehouse"), () => {
				new frappe.ui.Scanner({
					dialog: true,
					multiple: false,
					on_scan(data) {
						open_scanned_link(data.decodedText);
					},
				});
			});
		};
		tree.scan_button_added = true;
	}
})();