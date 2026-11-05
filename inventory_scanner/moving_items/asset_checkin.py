import frappe

from .common import (
	create_asset_movement,
	get_asset,
)


@frappe.whitelist()
def checkin_asset(asset_id, location=None):
	"""Check an asset back in by creating a Receipt Asset Movement.
	Only the employee who has the asset (its custodian) can check it in,
	unless the logged in user is an admin.  The asset goes to `location`
	if given, otherwise to the site's `inventory_scanner_checkin_location`
	setting.
	"""

	asset = get_asset(asset_id)

	if not asset.custodian:
		frappe.throw("Asset is not currently checked out.")

	employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
	# TODO: swap System Manager for the Admin role once roles are merged
	is_admin = "System Manager" in frappe.get_roles()

	if asset.custodian != employee and not is_admin:
		frappe.throw("Only the person who checked this asset out can check it in.")

	location = location or frappe.conf.get("inventory_scanner_checkin_location")

	if not location:
		frappe.throw("Check-in location has not been configured.")

	if not frappe.db.exists("Location", location):
		frappe.throw("Configured Asset Location does not exist.")

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
