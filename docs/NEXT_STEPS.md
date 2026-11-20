# Next steps for the next team

What we know is unfinished, untested or unconfirmed.  Items Marked *(to confirm)*
are our best reading and need checking before anyone builds on them.

## Requested by client

- **Custodian and check-in.** The client wasnt anybody to be able to check an item
back in, not only the person who checked it out.  ERPNext's Asset has a Custodian
field, which is proabbly where this belongs *(to confirm)*.  Today, who may check
in is decided in `moving_item/checkin_permissions.py` (with tests).  Work out 
what "anybody" means (any signed in user or any employee), what happens to 
Custodian field on check in, and whether the Asset Movement record should 
show who did it.

## Known gaps in code

- Receiving to a group location or warehouse can be refused.  Asset Repair has a
similar gap with group warehouses*(ton confirm th exact behavior)*.
- Shelf receiving does not support rejected quantities; a receipt row with one is
refused.
- A placement that reaches zero stays as a row at 0.  Decide whether empty rows
should be deleted.
- Item Placement is our own table.  Nothing reconciles its totals with ERPNext's
stock balance, so the two can drift apart.  A report comparing them would help
*(to confirm whether they drift in practice)*.

## Not verified

- The label sheet grid has not been checked on real 2" x 4" paper.  The numbers
are at the top of `label_sheet_layout.py`.
- The code that talks to the database (receive and cancel handlers, the label
sheet server method) has no automated tests.  Only the arithmetic and layout
math is covered.

## Setup the app does not do

- Operator, Technician and Viewer roles are not created by the app(`patches.txt`
is empty).  Create them on a new site.
- Each Asset Category needs an account row for every company, or Install Parts
fails with "Account required".
- ON the shared dev ERP, Item Placement permissions are custom rows that override
the app's JSON, and Technician can currently print everything.  Decide which
permissions belong in the app files, so a new site matches dev.
- The shared dev ERP has no wkhtmlopdf, so the PDF button on label formats fails.
wkhtmlopdf is removed in Frappe v17; the label formats will need to move to Chromium
before upgrading.

## Housekeeping

- Pre commit hooks (ruff, Prettier, ESLint) are not installed in everyone's clone,
so run `uvx pre-commit run --from-ref main --to-ref HEAD` before pushing.
- Test reocrds are mixed in with demo records on the dev ERP.  Clear out the test
data and record what the demo needs.
- The Computer Company row was removed from the Computers Asset Category on dev.
Check whether any asset still depends on it.