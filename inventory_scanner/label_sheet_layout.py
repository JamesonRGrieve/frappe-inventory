"""Layout for the 2" x 4" labels sheet: 10 labels, 2 columns x 5 rows, US Letter.

Kept free of any Frappe imports for unit tests using plain pytest.
All measurements in inches.
"""

COLUMNS = 2
ROWS = 5
CELLS_PER_SHEET = COLUMNS * ROWS

# Sheet measurements, matches Avery 5163 layout.  Print test page on plain
# paper and hold it against a real sheet;  adjust numbers where necessary
LABEL_WIDTH = 4.0
LABEL_HEIGHT = 2.0
LEFT_MARGIN = 0.15625
TOP_MARGIN = 0.5
COLUMN_GAP = 0.1875
ROW_GAP = 0.0


def place_labels(count, start_cell=1):
	"""Return a (sheet, row, column) tuple for each label, counted from 0.

	Cells are numbered left to right then down, so cell 1 is top left and
	cell 10 is bottom right.  If labels runs past cell 10 they continue
	on the next sheet at cell 1.
	"""
	if not 1 <= start_cell <= CELLS_PER_SHEET:
		raise ValueError(f"Start cell must be between 1 and {CELLS_PER_SHEET}")
	if count < 0:
		raise ValueError("Label count can't be negative")

	first_slot = start_cell - 1
	positions = []
	for index in range(count):
		sheet, cell = divmod(first_slot + index, CELLS_PER_SHEET)
		row, column = divmod(cell, COLUMNS)
		positions.append((sheet, row, column))
	return positions


def cell_offset(row, column):
	"""Return the (left, top) corner of a cell, in inches from the page's top left"""
	left = LEFT_MARGIN + column * (LABEL_WIDTH + COLUMN_GAP)
	top = TOP_MARGIN + row * (LABEL_HEIGHT + ROW_GAP)
	return left, top
