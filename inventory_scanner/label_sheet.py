"""Builds a printable sheet of QR labels for 2" x 4" label paper (10 per US Letter sheet)."""

import html
import re

import frappe
from frappe import _
from frappe.utils import cint, get_url_to_form

from inventory_scanner.label_sheet_layout import (
	LABEL_HEIGHT,
	LABEL_WIDTH,
	cell_offset,
	place_labels,
)
from inventory_scanner.labels import qr_data_uri

ALLOWED_DOCTYPES = ("Item", "Asset", "Location", "Warehouse")
MAX_LABELS = 200
DETAIL_LIMIT = 160

# For each DocType the field shown as the title, and the field shown as the description.
# Item has a real description. The others have less, so they show where the record sits.
LABEL_FIELDS = {
	"Item": ("item_name", "description"),
	"Asset": ("asset_name", "item_name"),
	"Location": ("location_name", "parent_location"),
	"Warehouse": ("warehouse_name", "parent_warehouse"),
}


@frappe.whitelist()
def get_label_sheet_html(doctype, names, start_cell=1):
	"""Return the html for a sheet of labels for the given records, starting at `start_cell`."""
	if doctype not in ALLOWED_DOCTYPES:
		frappe.throw(_("Labels can't be printed for {0}").format(doctype))

	names = frappe.parse_json(names)
	if not isinstance(names, list) or not names:
		frappe.throw(_("Select at least one record"))
	if len(names) > MAX_LABELS:
		frappe.throw(_("Select no more than {0} records at a time").format(MAX_LABELS))

	labels = []
	for name in names:
		# Same rule as the Print button, so roles without Print permission can't use this either.
		if not frappe.has_permission(doctype, "print", doc=name):
			frappe.throw(
				_("You don't have permission to print {0} {1}").format(doctype, name), frappe.PermissionError
			)
		labels.append(_label_data(doctype, name))

	return render_sheet(labels, cint(start_cell) or 1)


def _plain_text(value, limit):
	"""Strip html tags and extra whitespace, and shorten the text so it fits on a label."""
	text = html.unescape(re.sub(r"<[^>]*>", " ", value or ""))
	text = " ".join(text.split())
	if len(text) > limit:
		text = text[: limit - 1].rstrip() + "…"
	return text


def _label_data(doctype, name):
	title_field, detail_field = LABEL_FIELDS[doctype]
	doc = frappe.get_doc(doctype, name)

	title = _plain_text(doc.get(title_field), 80)
	if title == doc.name:
		title = ""  # Don't print the same text twice

	return {
		"name": doc.name,
		"title": title,
		"detail": _plain_text(doc.get(detail_field), DETAIL_LIMIT),
		"link": get_url_to_form(doctype, doc.name),
	}


def _label_html(label, left, top):
	parts = [f'<div class="name">{html.escape(label["name"])}</div>']
	if label["title"]:
		parts.append(f'<div class="title">{html.escape(label["title"])}</div>')
	if label["detail"] and label["detail"] != label["title"]:
		parts.append(f'<div class="detail">{html.escape(label["detail"])}</div>')
	text = "".join(parts)
	qr = qr_data_uri(label["link"])
	return (
		f'<div class="label" style="left:{left}in;top:{top}in">'
		f'<img src="{qr}"><div class="text">{text}</div></div>'
	)


STYLE = f"""
@page {{ size: 8.5in 11in; margin: 0; }}
body {{ margin: 0; font-family: sans-serif; }}
.toolbar {{ padding: 8px 12px; background: #f3f3f3; font-size: 13px; }}
.toolbar button {{ margin-right: 12px; }}
.sheet {{ position: relative; width: 8.5in; height: 11in; overflow: hidden; page-break-after: always; }}
.sheet:last-child {{ page-break-after: auto; }}
.label {{ position: absolute; width: {LABEL_WIDTH}in; height: {LABEL_HEIGHT}in; box-sizing: border-box;
  padding: 0.12in 0.15in; display: flex; align-items: center; gap: 0.12in; overflow: hidden; }}
.label img {{ width: 1.5in; height: 1.5in; flex: none; }}
.text {{ min-width: 0; }}
.name {{ font-size: 13pt; font-weight: bold; line-height: 1.15; overflow-wrap: anywhere;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
.title {{ font-size: 10pt; line-height: 1.2; margin-top: 2pt;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
.detail {{ font-size: 8.5pt; line-height: 1.2; margin-top: 2pt; color: #333;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }}
@media screen {{ .sheet {{ margin: 12px auto; box-shadow: 0 0 4px #999; }}
  .label {{ outline: 1px dashed #ccc; }} }}
@media print {{ .toolbar {{ display: none; }} }}
"""


def render_sheet(labels, start_cell):
	"""Lay the labels out on as many sheets as needed and return a complete html page."""
	sheets = {}
	for label, (sheet, row, column) in zip(labels, place_labels(len(labels), start_cell), strict=True):
		left, top = cell_offset(row, column)
		sheets.setdefault(sheet, []).append(_label_html(label, left, top))

	pages = "".join(f'<div class="sheet">{"".join(cells)}</div>' for _, cells in sorted(sheets.items()))
	toolbar = (
		'<div class="toolbar"><button onclick="window.print()">Print</button>'
		"Print at 100% scale (not &quot;fit to page&quot;) with margins set to None.</div>"
	)
	head = f'<meta charset="utf-8"><title>Label sheet</title><style>{STYLE}</style>'
	return f"<!DOCTYPE html><html><head>{head}</head><body>{toolbar}{pages}</body></html>"
