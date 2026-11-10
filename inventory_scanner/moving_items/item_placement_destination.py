import frappe
from frappe import _

from inventory_scanner.moving_items.item_placement_move import move_item_placement


def get_or_create_placement(item_code, location, warehouse):
	"""Return the Item Placement for this item, shelf and warehouse.

	Creates it with quantity 0 if it doesn't exist yet.
	"""
	name = f"{item_code}-{location}-{warehouse}"

	if frappe.db.exists("Item Placement", name):
		return name

	if not frappe.has_permission("Item Placement", "create"):
		frappe.throw(
			_("{0} isn't on {1} yet, and you aren't allowed to add it.").format(item_code, location),
			frappe.PermissionError,
		)

	try:
		frappe.get_doc(
			{
				"doctype": "Item Placement",
				"item_code": item_code,
				"location": location,
				"warehouse": warehouse,
				"quantity": 0,
			}
		).insert()
	except frappe.DuplicateEntryError:
		# Someone created the same row at the same moment. Use theirs.
		pass

	return name


@frappe.whitelist(methods=["POST"])
def move_to_location(source_placement, to_location, quantity):
	"""Move quantity from a placement to a shelf, creating the shelf's row if needed."""
	if not source_placement or not to_location:
		frappe.throw(_("Source placement and destination shelf are required."))

	source = frappe.get_doc("Item Placement", source_placement)
	source.check_permission("write")

	destination = get_or_create_placement(source.item_code, to_location, source.warehouse)

	return move_item_placement(source_placement, destination, quantity)
