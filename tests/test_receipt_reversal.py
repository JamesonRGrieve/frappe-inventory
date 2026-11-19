import unittest
from decimal import Decimal

from inventory_scanner.moving_items.receipt_reversal import calculate_remaining


class TestReceiptReversal(unittest.TestCase):
	def test_removes_exact_quantity(self):
		self.assertEqual(calculate_remaining(10, 10), Decimal("0"))

	def test_leaves_the_rest(self):
		self.assertEqual(calculate_remaining(10, 4), Decimal("6"))

	def test_decimal_quantities(self):
		self.assertEqual(calculate_remaining("2.5", "1.25"), Decimal("1.25"))

	def test_refuses_when_some_was_moved(self):
		with self.assertRaises(ValueError):
			calculate_remaining(4, 10)

	def test_zero_or_negative_quantity_rejected(self):
		with self.assertRaises(ValueError):
			calculate_remaining(10, 0)
		with self.assertRaises(ValueError):
			calculate_remaining(10, -1)

	def test_missing_current_quantity_counts_as_zero(self):
		with self.assertRaises(ValueError):
			calculate_remaining(None, 1)

	def test_invalid_input_rejected(self):
		with self.assertRaises(ValueError):
			calculate_remaining(10, "abc")
		with self.assertRaises(ValueError):
			calculate_remaining(10, float("nan"))
