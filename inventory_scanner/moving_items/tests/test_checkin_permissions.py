
import sys
import unittest
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch

try:
    import frappe
except ImportError:
    frappe = ModuleType("frappe")
    frappe.PermissionError = type("PermissionError", (Exception,), {})
    frappe.get_roles = MagicMock(return_value=[])
    frappe.session = SimpleNamespace(user="Guest")
    frappe.db = SimpleNamespace(get_value=MagicMock())
    frappe._ = lambda message: message

    def throw(message, exc=None):
        raise (exc or frappe.PermissionError)(message)

    frappe.throw = throw
    sys.modules["frappe"] = frappe

from inventory_scanner.moving_items.checkin_permissions import (
    verify_asset_checkin_permission,
)


class TestCheckinPermissions(unittest.TestCase):
    def setUp(self):
        self.asset = SimpleNamespace(custodian="HR-EMP-00001")

    @patch("frappe.get_roles", return_value=["Employee"])
    @patch("frappe.session")
    @patch("frappe.db.get_value", return_value="HR-EMP-00001")
    def test_same_employee_allowed(self, get_value, session, roles):
        session.user = "employee@example.com"

        verify_asset_checkin_permission(self.asset)

        get_value.assert_called_once_with(
            "Employee",
            {"user_id": "employee@example.com"},
            "name",
        )

    @patch("frappe.get_roles", return_value=["Employee"])
    @patch("frappe.session")
    @patch("frappe.db.get_value", return_value="HR-EMP-00002")
    def test_different_employee_rejected(self, get_value, session, roles):
        session.user = "other@example.com"

        with self.assertRaises(frappe.PermissionError):
            verify_asset_checkin_permission(self.asset)

    @patch("frappe.get_roles", return_value=["System Manager"])
    @patch("frappe.session")
    def test_system_manager_allowed(self, session, roles):
        session.user = "manager@example.com"

        verify_asset_checkin_permission(self.asset)

    @patch("frappe.get_roles", return_value=[])
    @patch("frappe.session")
    def test_administrator_allowed(self, session, roles):
        session.user = "Administrator"

        verify_asset_checkin_permission(self.asset)

    @patch("frappe.get_roles", return_value=["Employee"])
    @patch("frappe.session")
    @patch("frappe.db.get_value", return_value=None)
    def test_unlinked_user_rejected(self, get_value, session, roles):
        session.user = "unlinked@example.com"

        with self.assertRaises(frappe.PermissionError):
            verify_asset_checkin_permission(self.asset)


if __name__ == "__main__":
    unittest.main()
