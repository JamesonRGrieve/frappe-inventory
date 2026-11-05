
import frappe

from .checkin_permissions import verify_asset_checkin_permission
from .common import create_asset_movement, get_asset


@frappe.whitelist(methods=["POST"])
def checkin_asset(asset_id, location=None):
    """Check in an Asset to the selected or default Location."""

    # Get the Asset.
    asset = get_asset(asset_id)

    # Make sure the Asset is checked out.
    if not asset.custodian:
        frappe.throw("Asset is not currently checked out.")

    # Only the custodian or authorized admin can check it in.
    verify_asset_checkin_permission(asset)

    # Use the provided Location or configured default.
    location = location or frappe.conf.get(
        "inventory_scanner_checkin_location"
    )

    if not location:
        frappe.throw(
            "Check-in Location has not been configured."
        )

    if not frappe.db.exists("Location", location):
        frappe.throw(
            "The selected Asset Location does not exist."
        )

    # Create the ERPNext Asset Movement.
    result = create_asset_movement(
        asset,
        "Receipt",
        {
            "from_employee": asset.custodian,
            "target_location": location,
        },
    )

    result["location"] = location
    result["message"] = "Asset checked in successfully"

    return result

