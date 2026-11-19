import frappe
from frappe import _

from .receipt_reversal import calculate_remaining


def on_purchase_receipt_cancel(doc, method=None):
	"""Take a cancelled receipt's quantities back out of Item Placement.

	Mirrors on_purchase_receipt_submit: returns and rows without a shelf location were
	never placed, so they are skipped here too.  If the stock has since been moved or
	checked out, the cancel is refused, so a placement never claims more than is there.
	"""

	if doc.is_return:
		return

	for row in doc.items:
		shelf = row.get("custom_shelf_location")

		if not shelf or not row.stock_qty or row.stock_qty <= 0:
			continue

		remove_received_quantity(
			item_code=row.item_code,
			location=shelf,
			warehouse=row.warehouse,
			quantity=row.stock_qty,
		)


def remove_received_quantity(item_code, location, warehouse, quantity):
	"""Subtract a cancelled receipt quantity from one Item Placement row."""

	names = frappe.get_all(
		"Item Placement",
		filters={"item_code": item_code, "location": location, "warehouse": warehouse},
		pluck="name",
		limit_page_length=2,
	)

	if len(names) > 1:
		frappe.throw(_("Duplicate Item Placement rows already exist."))

	if not names:
		frappe.throw(
			_("Can't cancel: no Item Placement found for {0} on {1} in {2}. It may have been moved.").format(
				item_code, location, warehouse
			)
		)

	placement = frappe.get_doc("Item Placement", names[0])

	try:
		remaining = calculate_remaining(placement.quantity, quantity)
	except ValueError:
		frappe.throw(
			_(
				"Can't cancel: {0} on {1} in {2} has only {3} left, but this receipt added {4}. "
				"Undo the moves of this item first."
			).format(item_code, location, warehouse, placement.quantity, quantity)
		)

	# A placement that reaches zero stays as a row at 0, as the receive code does not delete rows either.
	placement.quantity = float(remaining)
	placement.save()
