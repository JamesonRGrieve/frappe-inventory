frappe.ui.form.on("Asset Capitalization", {
  refresh(frm) {
    if (frm.doc.docstatus === 0) {
      frm.add_custom_button(__("Install Items"), () => {
        new frappe.ui.Scanner({
          dialog: true,
          multiple: false,
          on_scan(data) {
            let scannedText = data.decodedText;
            let finalItemCode = scannedText;

            if (scannedText.startsWith("http://") || scannedText.startsWith("https://")) {
                let parts = scannedText.split('/');
                finalItemCode = parts[parts.length - 1];
            }
            finalItemCode = decodeURIComponent(finalItemCode);
            let row = frm.add_child("stock_items");
            row.item_code = finalItemCode;
            frm.refresh_field("stock_items");
            frm.script_manager.trigger("item_code", row.doctype, row.name);
          },
        });
      });
    }
  }
});

frappe.ui.form.on("Asset Capitalization", {
  refresh(frm) {
    if (frm.doc.docstatus === 0) { 
      frm.add_custom_button(__("Remove Items"), () => {
        new frappe.ui.Scanner({
          dialog: true,
          multiple: false,
          on_scan(data) {
            let scannedText = data.decodedText;
            let finalItemCode = scannedText;

            if (scannedText.startsWith("http://") || scannedText.startsWith("https://")) {
              let parts = scannedText.split('/');
              finalItemCode = parts[parts.length - 1];
            }
            finalItemCode = decodeURIComponent(finalItemCode);
            let targetRow = (frm.doc.stock_items || []).find(row => row.item_code === finalItemCode);

            if (targetRow) {
              frappe.model.clear_doc(targetRow.doctype, targetRow.name);
              
              frm.refresh_field("stock_items");
              frm.dirty();
              
            } else {
              frappe.msgprint(__("Scanned item is not on the list.", [finalItemCode]));
            }
          },
        });
      });
    }
  }
});

frappe.ui.form.on("Asset Repair", {
  refresh(frm) {
    if (frm.doc.docstatus === 0) {
      frm.add_custom_button(__("Repair Items"), () => {
        new frappe.ui.Scanner({
          dialog: true,
          multiple: false,
          on_scan(data) {
            let scannedText = data.decodedText;
            let finalItemCode = scannedText;

            if (scannedText.startsWith("http://") || scannedText.startsWith("https://")) {
                let parts = scannedText.split('/');
                finalItemCode = parts[parts.length - 1];
            }
            finalItemCode = decodeURIComponent(finalItemCode);
            let row = frm.add_child("stock_items");
            row.item_code = finalItemCode;
            frm.refresh_field("stock_items");
            frm.script_manager.trigger("item_code", row.doctype, row.name);
          },
        });
      });
    }
  }
});

frappe.ui.form.on("Asset Repair", {
	refresh(frm) {
		if (frm.doc.docstatus !== 0) return;
		const grid = frm.fields_dict.stock_items.grid;
		const btn = grid.add_custom_button(__("Scan Warehouse"), () => {
			const selected_rows = grid.get_selected_children();
			if (!selected_rows.length) {
				frappe.msgprint(__("Select the stock items to assign to a warehouse."));
				return;
			}
			new frappe.ui.Scanner({
				dialog: true,
				multiple: false,
				on_scan(data) {
					let scannedText = data.decodedText;
					let finalWarehouse = scannedText;

					if (scannedText.startsWith("http://") || scannedText.startsWith("https://")) {
						let parts = scannedText.split("/");
						finalWarehouse = parts[parts.length - 1];
					}
					finalWarehouse = decodeURIComponent(finalWarehouse);

					selected_rows.forEach((row) => {
						frappe.model.set_value(row.doctype, row.name, "warehouse", finalWarehouse);
					});
					frm.refresh_field("stock_items");
				},
			});
		});
		btn.addClass("scan-warehouse");
	},
});