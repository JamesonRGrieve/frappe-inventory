
import frappe
from frappe import _

from .item_placement_receive import add_received_quantity


def on_purchase_receipt_submit(doc, method=None):
    """Add accepted receipt quantities to Item Placement."""

    if doc.is_return:
        return

    for row in doc.items:
        shelf = row.get("custom_shelf_location")

        # Ordinary receipts without a shelf are not part of this workflow.
        if not shelf:
            continue

        if not row.item_code or not row.warehouse:
            frappe.throw(_("Item and Warehouse are required."))

        if not frappe.db.exists("Location", shelf):
            frappe.throw(_("Shelf Location does not exist."))

        if not frappe.db.exists("Warehouse", row.warehouse):
            frappe.throw(_("Warehouse does not exist."))

        if row.rejected_qty:
            frappe.throw(
                _("Rejected quantities are not supported for shelf receiving.")
            )

        qty = row.stock_qty

        if not qty or qty <= 0:
            frappe.throw(_("Received stock quantity must be positive."))

        add_received_quantity(
            item_code=row.item_code,
            location=shelf,
            warehouse=row.warehouse,
            quantity=qty,
        )
