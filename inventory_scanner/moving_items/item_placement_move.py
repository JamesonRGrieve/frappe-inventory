from decimal import Decimal, InvalidOperation

import frappe
from frappe import _


def calculate_move(source_quantity, destination_quantity, quantity):
	"""Calculate new quantities without allowing negative stock."""

	try:
		source = Decimal(str(source_quantity))
		destination = Decimal(str(destination_quantity))
		amount = Decimal(str(quantity))
	except InvalidOperation, TypeError, ValueError:
		raise ValueError("Quantities must be valid numbers.") from None

	if not all(value.is_finite() for value in (source, destination, amount)):
		raise ValueError("Quantities must be finite numbers.")

	if source < 0 or destination < 0:
		raise ValueError("Stored quantities cannot be negative.")

	if amount <= 0:
		raise ValueError("Move quantity must be greater than zero.")

	if amount > source:
		raise ValueError("Insufficient source quantity.")

	return source - amount, destination + amount


@frappe.whitelist(methods=["POST"])
def move_item_placement(
	source_placement,
	destination_placement,
	quantity,
):
	"""Transfer quantity between two Item Placement records."""

	if not source_placement or not destination_placement:
		frappe.throw(_("Source and destination placements are required."))

	if source_placement == destination_placement:
		frappe.throw(_("Source and destination must be different."))

	if not frappe.db.exists("DocType", "Item Placement"):
		frappe.throw(_("Item Placement DocType is not installed."))

	# Lock both records in consistent order.
	names = sorted((source_placement, destination_placement))

	locked = frappe.db.sql(
		"""
        SELECT name
        FROM `tabItem Placement`
        WHERE name IN (%s, %s)
        ORDER BY name
        FOR UPDATE
        """,
		names,
		as_dict=True,
	)

	if len(locked) != 2:
		frappe.throw(_("Source or destination placement was not found."))

	source = frappe.get_doc("Item Placement", source_placement)
	destination = frappe.get_doc(
		"Item Placement",
		destination_placement,
	)

	# Verify permissions.
	source.check_permission("write")
	destination.check_permission("write")

	if source.item != destination.item:
		frappe.throw(_("Placements must contain the same item."))

	try:
		new_source, new_destination = calculate_move(
			source.quantity,
			destination.quantity,
			quantity,
		)
	except ValueError as error:
		frappe.throw(str(error))

	# Update both placement quantities.
	source.quantity = float(new_source)
	destination.quantity = float(new_destination)

	source.save()
	destination.save()

	return {
		"success": True,
		"item": source.item,
		"from_location": source.location,
		"to_location": destination.location,
		"source_quantity": float(new_source),
		"destination_quantity": float(new_destination),
		"moved_quantity": float(Decimal(str(quantity))),
	}
