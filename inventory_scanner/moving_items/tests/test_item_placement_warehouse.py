from unittest.mock import MagicMock, patch

from inventory_scanner.moving_items.item_placement_move import move_item_placement

MODULE = "inventory_scanner.moving_items.item_placement_move"


def make_placement(warehouse, quantity):
	placement = MagicMock()
	placement.item_code = "ITEM-1"
	placement.warehouse = warehouse
	placement.quantity = quantity
	return placement


def run_move(source, destination):
	with (
		patch(f"{MODULE}.frappe") as mock_frappe,
		patch(f"{MODULE}._", lambda text: text),
	):
		mock_frappe.db.exists.return_value = True
		mock_frappe.db.sql.return_value = [{"name": "A"}, {"name": "B"}]
		mock_frappe.get_doc.side_effect = [source, destination]
		mock_frappe.throw.side_effect = RuntimeError
		try:
			return move_item_placement("A", "B", 2), mock_frappe
		except RuntimeError:
			return None, mock_frappe


def test_refuses_move_between_different_warehouses():
	source = make_placement("WH-A", 5)
	destination = make_placement("WH-B", 1)

	result, mock_frappe = run_move(source, destination)

	assert result is None
	assert "same warehouse" in mock_frappe.throw.call_args[0][0]
	source.save.assert_not_called()
	destination.save.assert_not_called()


def test_allows_move_within_one_warehouse():
	source = make_placement("WH-A", 5)
	destination = make_placement("WH-A", 1)

	result, _mock = run_move(source, destination)

	assert result["success"] is True
	assert source.quantity == 3
	assert destination.quantity == 3
	source.save.assert_called_once()
	destination.save.assert_called_once()
