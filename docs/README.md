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
bench get-app https://github.com/JamesonRGrieve/zephyrex-inventory --branch main
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


## Working on a feature

1. Pull the latest `main`, then branch from it (`yourname/feature`)
2. Make your changes in the app folder, `apps/inventory_scanner` in your bench
3. Before you push, run these from `apps/inventory_scanner`:
   ```
   uvx ruff format .
   uvx ruff check .
   ```
   CI runs the same checks, and a failure turns the pull request red.  Format runs
   first, so a formatting error hides any lint errors until it is fixed.  Python
   files use tabs, and `ruff format` converts spaces for you.
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

Standard print formats are only saved in the app's files when developer mode is on in
your bench:

```
bench --site dev.localhost set-config developer_mode 1
```

Restart `bench start` then create the print format with **Standard** checked
and Module set to Inventory Scanner.  Commit the new folder under
`inventory_scanner/inventory_scanner/print_format/`.

A print format belongs to one doctype, so each doctype needs its own QR label.  The
`qr_data_uri` helper in `labels.py` works for any text.  The link in the code is built
from the address you are browsing, so print labels from the real site: a label printed
on a local bench points at `localhost`.  After pulling new print formats, run `migrate`.
If a format is renamed, the old record stays on sites that already had it.

## Troubleshooting

- **`yarn` not found during `bench init`:** `npm install -g yarn`, answer `y` to
   roll back the partial bench, and run `bench init` again
- **Error 1698, "Access denied for user 'root'@'localhost'":** the MariaDB root
   password is not set or was mistyped.  Repeat step 2 and run the test command
- **"Connection refused" on port 11000 or 13000 while installing ERPNext:** Redis
   is not running.  Start `bench start` in another window and retry.
   