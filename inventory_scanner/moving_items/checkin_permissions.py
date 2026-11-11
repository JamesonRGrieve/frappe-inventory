
import frappe


def verify_asset_checkin_permission(asset):
    """
    Allow the current custodian to check in an Asset.

    Administrator or a user with the System Manager role can
    check in an Asset on behalf of another Employee.

    The Asset's custodian must be an Employee document ID.
    """
    user = frappe.session.user

    # Only trusted administrative users can override custody.
    if user == "Administrator" or "System Manager" in frappe.get_roles(user):
        return

    if not asset.custodian:
        frappe.throw(
            _("Asset has no current custodian. Contact an administrator."),
            frappe.PermissionError,
        )

    employee = frappe.db.get_value(
        "Employee",
        {"user_id": user},
        "name",
    )

    if not employee:
        frappe.throw(
            _("Your user account is not linked to an Employee."),
            frappe.PermissionError,
        )

    if employee != asset.custodian:
        frappe.throw(
            _("Only the current custodian or an administrator can check in this Asset."),
            frappe.PermissionError,
        )
