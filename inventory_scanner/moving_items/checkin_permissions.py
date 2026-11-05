import frappe
from frappe import _


def verify_asset_checkin_permission(asset):
	"""Allow the current custodian or an authorized admin to check in."""

	user = frappe.session.user

	# Administrator and System Managers can check in
	# assets on behalf of another employee.
	if user == "Administrator" or "System Manager" in frappe.get_roles(user):
		return

	if not asset.custodian:
		frappe.throw(
			_("Asset has no current custodian."),
			frappe.PermissionError,
		)

	# Get the Employee linked to the logged-in User.
	employee = frappe.db.get_value(
		"Employee",
		{"user_id": user},
		"name",
	)

	if not employee:
		frappe.throw(
			_("Your account is not linked to an Employee."),
			frappe.PermissionError,
		)

	if employee != asset.custodian:
		frappe.throw(
			_("Only the current custodian or an authorized administrator can check in this Asset."),
			frappe.PermissionError,
		)
