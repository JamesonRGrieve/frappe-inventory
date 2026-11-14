from decimal import Decimal, InvalidOperation

import frappe
from frappe import _


def add_received_quantity(item_code, location, warehouse, quantity):
	"""Create or update one Item Placement row."""

	if not all([item_code, location, warehouse]):
		frappe.throw(_("Item, shelf and warehouse are required."))

	try:
		received = Decimal(str(quantity))
	except InvalidOperation, TypeError, ValueError:
		frappe.throw(_("Invalid received quantity."))

	if not received.is_finite() or received <= 0:
		frappe.throw(_("Received quantity must be positive."))

	filters = {
		"item_code": item_code,
		"location": location,
		"warehouse": warehouse,
	}

	# Search first instead of always inserting.
	names = frappe.get_all(
		"Item Placement",
		filters=filters,
		pluck="name",
		limit_page_length=2,
	)

	if len(names) > 1:
		frappe.throw(_("Duplicate Item Placement rows already exist."))

	if names:
		placement = frappe.get_doc("Item Placement", names[0])

		current = Decimal(str(placement.quantity or 0))
		if not current.is_finite() or current < 0:
			frappe.throw(_("Invalid existing placement quantity."))

		placement.quantity = float(current + received)
		placement.save()

		action = "updated"

	else:
		placement = frappe.get_doc(
			{
				"doctype": "Item Placement",
				"item_code": item_code,
				"location": location,
				"warehouse": warehouse,
				"quantity": float(received),
			}
		)

		placement.insert()
		action = "created"

	return {
		"action": action,
		"name": placement.name,
		"quantity": placement.quantity,
	}
