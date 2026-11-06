"""Stand in for frappe so unit test run in CI, where
only pytest is installed.

If the real frappe is importable (on a bench), nothing changes.
"""

import sys
import types
from unittest.mock import MagicMock

try:
	import frappe
except ModuleNotFoundError:
	stub = types.ModuleType("frappe")

	stub.PermissionError = type("PermissionError", (Exception,), {})
	stub.ValidationError = type("ValidationError", (Exception,), {})

	def whitelist(*args, **kwargs):
		"""Behave like @frappe.whitelist and @frappe.whitelist(...)."""
		if len(args) == 1 and callable(args[0]) and not kwargs:
			return args[0]
		return lambda fn: fn

	def throw(message, exc=None, *args, **kwargs):
		raise (exc or stub.ValidationError)(message)

	stub.whitelist = whitelist
	stub.throw = throw
	stub._ = lambda text, *args, **kwargs: text
	stub.get_roles = MagicMock(return_value=[])
	stub.session = types.SimpleNamespace(user="Guest")
	stub.conf = {}
	stub.db = MagicMock()
	stub.get_doc = MagicMock()

	sys.modules["frappe"] = stub
