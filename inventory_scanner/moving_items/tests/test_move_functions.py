
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from inventory_scanner.moving_items.move_items_in import move_items_in
from inventory_scanner.moving_items.move_items_out import move_items_out


class TestMoveFunctions(unittest.TestCase):
    def setUp(self):
        self.item = SimpleNamespace(
            name="GM-TEST-STOCK-001",
            has_serial_no=0,
            has_batch_no=0,
        )
        self.source = SimpleNamespace(name="Stores - U")
        self.destination = SimpleNamespace(
            name="Finished Goods - U"
        )

        self.validated = (
            self.item,
            self.source,
            self.destination,
            1.0,
        )

    @patch(
        "inventory_scanner.moving_items.move_items_out."
        "create_stock_transfer"
    )
    @patch(
        "inventory_scanner.moving_items.move_items_out."
        "validate_stock_move"
    )
    def test_move_items_out(self, validate, transfer):
        validate.return_value = self.validated
        transfer.return_value = {
            "success": True,
            "stock_entry": "TEST-TRANSFER-001",
        }

        result = move_items_out(
            from_warehouse="Stores - U",
            item_code="GM-TEST-STOCK-001",
            to_warehouse="Finished Goods - U",
            qty=1,
        )

        validate.assert_called_once_with(
            "GM-TEST-STOCK-001",
            "Stores - U",
            "Finished Goods - U",
            1,
        )
        transfer.assert_called_once_with(
            self.item,
            self.source,
            self.destination,
            1.0,
        )
        self.assertTrue(result["success"])
        self.assertEqual(
            result["message"], "Items moved out successfully"
        )

    @patch(
        "inventory_scanner.moving_items.move_items_in."
        "create_stock_transfer"
    )
    @patch(
        "inventory_scanner.moving_items.move_items_in."
        "validate_stock_move"
    )
    def test_move_items_in(self, validate, transfer):
        validate.return_value = self.validated
        transfer.return_value = {
            "success": True,
            "stock_entry": "TEST-TRANSFER-002",
        }

        result = move_items_in(
            to_warehouse="Finished Goods - U",
            item_code="GM-TEST-STOCK-001",
            from_warehouse="Stores - U",
            qty=1,
        )

        validate.assert_called_once_with(
            "GM-TEST-STOCK-001",
            "Stores - U",
            "Finished Goods - U",
            1,
        )
        transfer.assert_called_once_with(
            self.item,
            self.source,
            self.destination,
            1.0,
        )
        self.assertTrue(result["success"])
        self.assertEqual(
            result["message"], "Items moved in successfully"
        )

    def test_serialized_items_are_rejected_in_move_out(self):
        self.item.has_serial_no = 1

        with patch(
            "inventory_scanner.moving_items.move_items_out."
            "validate_stock_move",
            return_value=self.validated,
        ), patch(
            "inventory_scanner.moving_items.move_items_out."
            "frappe.throw",
            side_effect=ValueError,
        ):
            with self.assertRaises(ValueError):
                move_items_out(
                    "Stores - U",
                    "GM-TEST-STOCK-001",
                    "Finished Goods - U",
                    1,
                )


if __name__ == "__main__":
    unittest.main()
