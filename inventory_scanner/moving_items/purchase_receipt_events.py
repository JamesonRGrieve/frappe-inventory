import frappe
from frappe import _

from .item_placement_receive import add_received_quantity


def on_purchase_receipt_submit(doc, method=None):
	"""Update shelf quantities when a Purchase Receipt is submitted."""

	for row in doc.items:
		shelf = row.get("custom_shelf_location")

		# Receipts without a shelf are outside this workflow.
		if not shelf:
			continue

		if not row.item_code or not row.warehouse:
			frappe.throw(_("Received Item and Warehouse are required."))

		if not frappe.db.exists("Location", shelf):
			frappe.throw(_("Shelf Location {0} does not exist.").format(shelf))

		if not frappe.db.exists("Warehouse", row.warehouse):
			frappe.throw(_("Warehouse does not exist."))

		# Stock quantity, not necessarily purchase UOM quantity.
		received_qty = row.stock_qty or 0

		# Reject rejected-stock rows until this workflow handles
		# their separate warehouse and quantity correctly.
		if row.rejected_qty:
			frappe.throw(_("Shelf receiving does not support rejected items yet."))

		if doc.is_return:
			frappe.throw(_("Shelf receiving does not support returns yet."))

		add_received_quantity(
			item_code=row.item_code,
			location=shelf,
			warehouse=row.warehouse,
			quantity=received_qty,
		)
