
from decimal import Decimal, InvalidOperation

import frappe
from frappe import _
from .item_placement_receive import add_received_quantity


def add_received_quantity(item, location, warehouse, quantity):
    """Create or update an Item Placement after receiving stock."""

    if not item or not location or not warehouse:
        frappe.throw(
            _("Item, Location, and Warehouse are required.")
        )

    try:
        received_qty = Decimal(str(quantity))
    except (InvalidOperation, TypeError, ValueError):
        frappe.throw(_("Invalid received quantity."))

    if not received_qty.is_finite() or received_qty <= 0:
        frappe.throw(_("Received quantity must be positive."))

    # Check whether the item already exists on this shelf.
    existing_rows = frappe.get_all(
        "Item Placement",
        filters={
            "item": item,
            "location": location,
            "warehouse": warehouse,
        },
        pluck="name",
        limit_page_length=2,
    )

    if len(existing_rows) > 1:
        frappe.throw(
            _("Duplicate Item Placement rows already exist.")
        )

    if existing_rows:
        # Update the existing placement.
        placement = frappe.get_doc(
            "Item Placement", existing_rows[0]
        )

        current_qty = Decimal(str(placement.quantity or 0))

        if not current_qty.is_finite() or current_qty < 0:
            frappe.throw(
                _("Existing placement quantity is invalid.")
            )

        placement.quantity = float(
            current_qty + received_qty
        )
        placement.save()

        action = "updated"

    else:
        # Create a placement only when none exists.
        placement = frappe.get_doc(
            {
                "doctype": "Item Placement",
                "item_code": item,
                "location": location,
                "warehouse": warehouse,
                "quantity": float(received_qty),
            }
        )
        placement.insert()

        action = "created"

    return {
        "success": True,
        "action": action,
        "placement": placement.name,
        "item_code": item,
        "location": location,
        "warehouse": warehouse,
        "quantity": placement.quantity,
    }
