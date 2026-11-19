import unittest

from inventory_scanner.label_sheet_layout import (
	CELLS_PER_SHEET,
	LABEL_HEIGHT,
	LABEL_WIDTH,
	LEFT_MARGIN,
	TOP_MARGIN,
	cell_offset,
	place_labels,
)


class TestLabelSheetLayout(unittest.TestCase):
	def test_first_cell_is_top_left(self):
		self.assertEqual(place_labels(1, 1), [(0, 0, 0)])

	def test_cells_number_left_to_right_then_down(self):
		self.assertEqual(place_labels(1, 2), [(0, 0, 1)])
		self.assertEqual(place_labels(1, 3), [(0, 1, 0)])
		self.assertEqual(place_labels(1, 10), [(0, 4, 1)])

	def test_labels_continue_onto_next_sheet_at_cell_one(self):
		self.assertEqual(place_labels(3, 9), [(0, 4, 0), (0, 4, 1), (1, 0, 0)])

	def test_full_sheet_uses_one_sheet(self):
		positions = place_labels(10, 1)
		self.assertEqual({sheet for sheet, _, _ in positions}, {0})
		self.assertEqual(len(set(positions)), 10)

	def test_eleventh_label_starts_second_sheet(self):
		self.assertEqual(place_labels(11, 1)[-1], (1, 0, 0))

	def test_no_labels(self):
		self.assertEqual(place_labels(0, 5), [])

	def test_start_cell_out_of_range_rejected(self):
		with self.assertRaises(ValueError):
			place_labels(1, 0)
		with self.assertRaises(ValueError):
			place_labels(1, CELLS_PER_SHEET + 1)

	def test_grid_fits_on_letter_paper(self):
		left, top = cell_offset(4, 1)
		self.assertAlmostEqual(cell_offset(0, 0)[0], LEFT_MARGIN)
		self.assertAlmostEqual(cell_offset(0, 0)[1], TOP_MARGIN)
		self.assertLessEqual(left + LABEL_WIDTH, 8.5)
		self.assertLessEqual(top + LABEL_HEIGHT, 11.0)
