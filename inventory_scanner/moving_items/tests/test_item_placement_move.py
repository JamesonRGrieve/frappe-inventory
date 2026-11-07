import unittest
from decimal import Decimal

from inventory_scanner.moving_items.item_placement_move import (
	calculate_move,
)


class TestItemPlacementMove(unittest.TestCase):
	def test_successful_move(self):
		source, destination = calculate_move(10, 5, 3)

		self.assertEqual(source, Decimal("7"))
		self.assertEqual(destination, Decimal("8"))

	def test_insufficient_source_quantity(self):
		with self.assertRaises(ValueError):
			calculate_move(2, 5, 3)

	def test_zero_quantity_rejected(self):
		with self.assertRaises(ValueError):
			calculate_move(10, 5, 0)

	def test_negative_quantity_rejected(self):
		with self.assertRaises(ValueError):
			calculate_move(10, 5, -1)

	def test_decimal_move(self):
		source, destination = calculate_move("2.5", "1.5", "0.5")

		self.assertEqual(source, Decimal("2.0"))
		self.assertEqual(destination, Decimal("2.0"))

	def test_invalid_quantity(self):
		with self.assertRaises(ValueError):
			calculate_move(10, 5, "invalid")

	def test_total_preserved(self):
		source, destination = calculate_move(10, 5, 3)

		self.assertEqual(
			source + destination,
			Decimal("15"),
		)


if __name__ == "__main__":
	unittest.main()
