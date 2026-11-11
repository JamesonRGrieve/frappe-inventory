
import frappe

from .checkin_permissions import verify_asset_checkin_permission
from .common import create_asset_movement, get_asset


@frappe.whitelist()
def  checkin_asset(asset_id, location=None):
    """Check in an Asset and return it to the configured Location."""

    # Step 1: Get the Asset.
    asset = get_asset(asset_id)

    # Step 2: Ensure the Asset is currently checked out.
    if not asset.custodian:
        frappe.throw("Asset is not currently checked out.")

    # Step 3: Verify the current user is allowed to check it in.
    # The custodian or an authorized administrator may check it in.
    verify_asset_checkin_permission(asset)

    # Step 4: Get the configured return Location.
    location = location or frappe.conf.get(
    "inventory_scanner_checkin_location"
    )

    if not location:
        frappe.throw(
            "Check-in location has not been configured."
        )

    # Step 5: Verify the Location exists.
    if not frappe.db.exists("Location", location):
        frappe.throw(
            "Configured Asset Location does not exist."
        )

    # Step 6: Create the Asset Movement.
    result = create_asset_movement(
        asset,
        "Receipt",
        {
            "from_employee": asset.custodian,
            "target_location": location,
        },
    )

    # Step 7: Return the result.
    result["location"] = location
    result["message"] = "Asset checked in successfully"

    return result
