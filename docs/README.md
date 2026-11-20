# inventory_scanner

A Frappe app for tracking inventory and assets on ERPNext, with QR code scanning
from a phone. ERPNext is the source of truth. This app adds the scanning and
action screens (receive, move, check in/out, install a part, asset history).

Built for the capstone project. Pushes to `main` that pass the tests deploy to
the shared dev ERP.

## Project documents

The scope document and ERD live in Google so they stay current:
- [Scope document](https://docs.google.com/document/d/1Y3Yyrwu-8Ov8PBTKOG0rJuDqYykgzGftyKkagmUSlAY/edit)
- [ERD](https://app.diagrams.net/#G1QbdqUgFpGbR4URTYSq6NJ74gAzfr3BBD#%7B%22pageId%22%3A%223yvbSbNHLUD0FFQW6qgT%22%7D)

## Guide for dev team

Each of us runs our own copy of the system on our computer (a "local bench").  
You build and test your feature there, where mistakes only affect you, and then
open a pull request.  Once it is merged into `main`, the shared dev ERP updates.

By the end of the guide you will have a local site at http://localhost:8000 with
Frappe, ERPNext and this app installed, matching the shared dev ERP.

Tested on Ubuntu 24.04 under WSL2 (Windows).  Mac and native Linux steps differ
and have not been tried.


## 1. Install requirements


Frappe v16 needs Python 3.14, Node 24, MariaDB 11.8 and Redis.  Check what you
have:

```
python3.14 --version
node -v
mariadb --version
redis-server --version
uv --version
```

Install what is missing:

1. **Python 3.14:** `uv python install 3.14 --default`
2. **Node 24 and yarn:** install nvm if you don't have it
   (`curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash`,
   then open a new terminal), then `nvm install 24`, then `npm install -g yarn`
   (without yarn, `bench init` fails with "No such file or directory: 'yar'")
3. **Redis and build tools:** `sudo apt install -y redis-server pkg-config`
4. **MariaDB 11.8:** Ubuntu 24.04 ships 10.11, so add MariaDB's own repository.
   Open https://mariadb.org/download/?t=repo-config, choose Ubuntu, 24.04 "noble",
   11.8, run the commands it gives you, then 
   `sudo apt install mariadb-server mariadb-client`.
  **If you already have databases in MariaDB, back them up first:**
  `sudo mariadb-dump --all-databases > ~/mariadb-backup.sql`


## 2. Give MariaDB a root password

Bench logs in to MariaDB as root with a password.  On Ubuntu the root account has
none, so set one (keep the socket login working too).  Use a password that is only
for this local database:

```
sudo mariadb -e "ALTER USER 'root'@'localhost' IDENTIFIED VIA mysql_native_password
USING PASSWORD('LocalPasswordHere') or unix_socket;"
```

Avoid '!' in this command, since the shell will refuse it.

## 3. Create the bench

Keep it outside this repo and outside `/mnt/c`:

```
uv tool install frappe-bench
mkdir -p ~/frappe && cd ~/frappe
bench init --frappe-branch version-16 --python3.14 frappe-bench
```

This will take a few minutes.

## 4. Start the bench, then create site

Open two terminal windows

**Window 1** (leave it running the whole time):
```
cd ~/frappe/frappe-bench
bench start
```

**Window 2** 

```
cd ~/frappe/frappe-bench
bench get-app erpnext --branch version-16
bench new-site dev.localhost --install-app erpnext
bench use dev.localhost
```

`bench new-site` asks for the MariaDB root password (step 2) and a new
Administrator password for the site.  Type both at the prompts.

If `bench new-site` fails partway, answer `y` when it asks whether to roll back the site.

`bench start` must be running before ERPNext install, because the install
queues a background job through Redis.

## 5. Get the app

```
cd ~/frappe/frappe-bench
bench get-app https://github.com/JamesonRGrieve/frappe-inventory --branch main
bench --site dev.localhost install-app inventory_scanner
bench --site dev.localhost list-apps
```

`list-apps` should show `frappe`, `erpnext` and `inventory_scanner`

## 6. Open the site

Go to http://localhost:8000 and sign in as 'Administrator' with the password you chose.
The setup wizard asks for language, country, time zone and currency, then company 
details.  This is the local test site, so keep it simple: Canada, CAD, America/Edmonton.
Check `/app/installed-applications` to confirm the three apps.

Stop the bench with Ctrl+C in window 1.

## Installing on an existing ERPNext site

This is for adding the app to a site that already runs ERPNext, such as a production
instance, rather than building a new local bench.

Requirements: Frappe and ERPNext on `version-16`, already installed on teh site.

```
cd ~/frappe-bench
bench get-app https://github.com/JamesonRGrieve/frappe-inventory --branch main
bench --site <your-site> install-app inventory_scanner
bench --site <your-site> migrate
bench build --app inventory_scanner
bench restart
```

The repository is called `frappe-inventory`, but the app name used by `install-app`
is `inventory_scanner`.  Confirm with `bench --site <your-site> list-apps`.

Installing adds the Item Placement doctype, a Shelf Location field on Purchase
Receipt items, the QR label print formats and the scan screens.  To update later, 
pull `main` in `apps/inventory_scanner`, run `migrate`, `bench build --app 
inventory_scanner`, and restart.

### After installing

The app does not do these for you:
1. **Roles** The permissions use the standard Stock User, Stock Manager and 
System Manager roles plus Operator, Technician, and Viewer.  If any of the
last three are missing in the Role list, create them.
2. **Asset Category accounts** InstallParts and similar actions on assets create
accounting entries.  Each Asset Category needs a row for every company with all 
four filled in (Fixed Asset, Accumulated Depreciation, Depreciation Expense and
Capital Work in Progress).  A missing row gives "Account required", and an account
that belongs to another compnay gives "does not belong to company".
3. **Purchase Receipt users** Anyone submitting a receipt who is not an administrator
needs the Purchase User role as well, or the submit fails with an account permission
error.
4. **QR label links** Lables link to the address the site is reached on.  To make
them always use the public address, run
`bench --site <your-site> set-config host_name "https://your-erp-address"`.
5 **PDF output.** The PDF button on the label formats needs wkhtmlopdf with patched
Qt on the server.  Without it the PDF fails, but the browser's Print option and 
the Label sheet still work.

## Working on a feature

1. Pull the latest `main`, then branch from it (`yourname/feature`)
2. Make your changes in the app folder, `apps/inventory_scanner` in your bench
3. Before you push, run these from `apps/inventory_scanner`:
   ```
   uvx ruff format .
   uvx ruff check .
   uv run --no-project --python 3.14 --with pytest python -I -m pytest
   ```
   CI runs the same checks, and a failure turns the pull request red.  Format runs
   first, so a formatting error hides any lint errors until it is fixed.  Python
   files use tabs, and `ruff format` converts spaces for you.

   The repo also has pre-commit hooks for ruff, Prettier and ESLint.  To run them
   on everything your branch changed:
   ```
   uvx pre-commit run --from-ref main --to-ref HEAD
   ```
   If a hook reformats a file, commit the change and run it again until every line
   passes.
4. Commit, push, and open a pull request.  Get one approval.  The pipeline runs ruff
   and pytest on every push and pull request.
5. Wait for the checks to go green before merging.  GitHub will let you merge a red check,
   so it is up to us not to.
6. After a merge, open
   https://dev-erp.jamesonrgrieve.ca/api/method/git_deploy.api.status?app=inventory_scanner
   and wait for "succeeded" before the next merge.  A green check in GitHub only means
   the deploy was queued.
7. Pull `main` into your bench and run `bench --site dev.localhost migrate`

## Conventions

- On the shared dev ERP, prefix anything you create with your initials.  Test data 
   uses its own prefix
- Custom fields and scripts are written into the app's files on the same
  branch as the feature that needs them.

## Print formats and QR labels

Each label encodes a link to its record, so scanning it opens that record.

| DocType | Print format | Size |
| --- | --- | --- |
| Asset | Asset QR Label | 50 x 60 mm |
| Item | Item QR Label | 50 x 60 mm |
| Item | Item QR Label 12mm | 14 x 20 mm, for small parts |
| Location | Location QR Label | 50 x60 mm |
| Warehouse | Warehouse QR Label | 50 x 60 mm |

The 12mm format has a 12mm QR code, which was tested for scanning on small
parts such as RAM sticks.

Standard print formats are only saved in the app's files when developer mode
is on in your bench:

```
bench --site dev.localhost set-config developer_mode 1
```

Restart `bench start` then create the print format with **Standard** checked
and Module set to Inventory Scanner.  Commit the new folder under
`inventory_scanner/inventory_scanner/print_format/`.

A print format belongs to one doctype, so each doctype needs its own QR label.
The `qr_data_uri` helper in `labels.py` works for any text.  The link in the code
is built from the address your are browswing, so print labels from the real site:
a label printed on a local bench points at `localhost`.  After pulling new print
formats, run `migrate`.  If a format is renamed, the old record stays on sites
that already had it.

`migrate` only reloads a print format file when its `modified` timestamp is newer
than the saved record, so update `modified` whenever you edit one by hand.

### Printing a shee of labels (2" x 4")

For label paper that is 2" x 4", 10 per US Letter sheet(2 columns x 5 rows):

1. Open the Item, Asset, Location or Warehouse list and tick the records.
2. Choose **Actions → Print Label Sheet**.
3. Pick the **start cell**, 1 to 10, to reuse a partly used sheet.  Cells are
numbered left to right, then down.  1 is top left, 10 is bottom right.
4. A sheet opens in a new tab.  Print it at 100% scale (not "fit to page") on
Letter paper with margins set to None.

If there are more labels than free cells, they continue on a second sheet
starting at cell 1.  Each label shows a QR code, the record name, and a title, 
or description where the record has one.  You need Print permission on each
record you select.  The sheet opens in a new tab with no address, so 
refreshing that tab empties it; run the action again instead.

The sheet layout (margins and gaps) is set by the constants at the top of
`inventory_scanner/label_sheet_layout.py`, based on the common Avery 5163 layout.
Print a test page on plain paper and hold it against a real sheet before using
real labels.  If it is off adjust those numbers.

## Receiving stock to a shelf

A Purchase Receipt row with a **Shelf Location** adds its quantity to the Item
Placement for that item, shelf and warehouse (creating the row if there isn't
one).  Rows with no shelf location, and return receipts, are ignored.  A row
with a rejected quantity is refused, since shelf receiving does not support it.

Cancelling the receipt takes the same quantities back out.  If some of that stock
has since been moved or checked out, the cancel is refused with a message naming
the item, shelf and warehouse.  Undo those first then cancel.  A placement reaches
zero stays as row at 0.

## Known Gaps

- Receiving to a group location or warehouse (one with child records) can be refused.
Use a leaf location, one with no expand arrow in the Location tree.
- Item Placement permissions in the app files can be overridden on a site.  Custom rows
saved in the Role Permissions Manager take priority over the app's JSON.
- The label sheet layout is based on the common Avery 5163 grid that has not been
checked against every brand of 2" x 4" paper. Print a test page before using real labels.


## Troubleshooting

- **`yarn` not found during `bench init`:** `npm install -g yarn`, answer `y` to
   roll back the partial bench, and run `bench init` again
- **Error 1698, "Access denied for user 'root'@'localhost'":** the MariaDB root
   password is not set or was mistyped.  Repeat step 2 and run the test command
- **"Connection refused" on port 11000 or 13000 while installing ERPNext:** Redis
   is not running.  Start `bench start` in another window and retry.
- **Account required** or "does not belong to company" on Install Parts:** the
Asset Cateogry has no row for the company, or its accounts belong to another company.
Add a row for the compnay with all four accounts.
- **"Invalid Request" after signing out:** a stale session cookie.  In browser DevTools
open Application > Storage and choose Clear site data.  If you sign in with single sign-on
you are signed straigh back in until you also sign out of the identity provider.
- **PDF button fails with wkhtmltopdf error:** the server does not have wkhtmltopdf with
patched Qt.  Use the browser's Print opion instead.  
   