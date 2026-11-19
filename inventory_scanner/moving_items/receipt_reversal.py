"""Quantity maths for taking a cancelled receipt back out of Item Placement.

Kept free of Frappe imports so it can be unit tested with plain pytest.
"""

from decimal import Decimal, InvalidOperation


def calculate_remaining(current, quantity):
	"""Return what is left in a placement after removing `quantity` from `current`.

	Raises ValueError if `quantity` is not a positive number, or if the placement holds
	less than `quantity` (some of it has already been moved or checked out).
	"""
	try:
		current = Decimal(str(current or 0))
		quantity = Decimal(str(quantity))
	except (InvalidOperation, TypeError, ValueError) as error:
		raise ValueError("Invalid quantity") from error

	if not quantity.is_finite() or quantity <= 0:
		raise ValueError("Quantity to remove must be positive")
	if not current.is_finite() or current < 0:
		raise ValueError("Invalid existing placement quantity")
	if current < quantity:
		raise ValueError("Not enough in this placement to remove")

	return current - quantity
