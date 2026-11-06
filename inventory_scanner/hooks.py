app_name = "inventory_scanner"
app_title = "Inventory Scanner"
app_publisher = "Ajay Paterson, Johnny Kwan, Michael Hubel, Robel Measho, Grishma Mistry"
app_description = "Inventory and asset tracking with QR scanning on ERPNext"
app_email = "ajay.paterson@gmail.com"
app_license = "AGPL-3.0-or-later"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "inventory_scanner",
# 		"logo": "/assets/inventory_scanner/logo.png",
# 		"title": "Inventory Scanner",
# 		"route": "/inventory_scanner",
# 		"has_permission": "inventory_scanner.api.permission.has_app_permission",
# 	}
# ]

# The dock, the rail down the left of the desk, is a document rather than a hook. Author it in
# Manage Dock on a developer-mode site and press Export to App, and it is written to
# `inventory_scanner/dock/inventory_scanner/inventory_scanner.json` for git to carry. An app that ships none has no
# rail: its sidebar gets a switcher in the header instead.
#
# A companion app, one that extends a host app rather than standing on its own, says so with
# `mount_on` on that same record, and its entries are appended to the host's rail. Mounting keeps
# the companion off the apps screen, so it takes precedence over any add_to_apps_screen above.

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/inventory_scanner/css/inventory_scanner.css"
# app_include_js = "/assets/inventory_scanner/js/inventory_scanner.js"

# include js, css files in header of web template
# web_include_css = "/assets/inventory_scanner/css/inventory_scanner.css"
# web_include_js = "/assets/inventory_scanner/js/inventory_scanner.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "inventory_scanner/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Warehouse": ["public/js/move.js"],
	"Asset": ["public/js/install.js"],
	"Asset Capitalization": ["public/js/parts.js"],
	"Item": ["public/js/receive.js"],
}
doctype_list_js = {
	"Warehouse": ["public/js/scan.js"],
	"Item": ["public/js/scan.js"],
	"Asset": ["public/js/scan.js"],
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_kanban_js = {"doctype" : "public/js/doctype_kanban.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "inventory_scanner/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "inventory_scanner.utils.jinja_methods",
# 	"filters": "inventory_scanner.utils.jinja_filters"
# }
jinja = {"methods": ["inventory_scanner.labels.qr_data_uri"]}

# Installation
# ------------

# before_install = "inventory_scanner.install.before_install"
# after_install = "inventory_scanner.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "inventory_scanner.uninstall.before_uninstall"
# after_uninstall = "inventory_scanner.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "inventory_scanner.utils.before_app_install"
# after_app_install = "inventory_scanner.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "inventory_scanner.utils.before_app_uninstall"
# after_app_uninstall = "inventory_scanner.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "inventory_scanner.build.after_build"

# To hook into the build process of other apps
# The list of apps being built is passed as an argument

# after_app_build = "inventory_scanner.build.after_app_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "inventory_scanner.notifications.get_notification_config"

# Awesome Bar
# -----------
# Extra search results: list of dicts with label, description, route, index.
# route: ["List", "ToDo"], "/desk/docs/some/page", or "https://example.com"
# awesomebar_search = ["inventory_scanner.search.awesomebar_results"]

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"inventory_scanner.tasks.all"
# 	],
# 	"daily": [
# 		"inventory_scanner.tasks.daily"
# 	],
# 	"hourly": [
# 		"inventory_scanner.tasks.hourly"
# 	],
# 	"weekly": [
# 		"inventory_scanner.tasks.weekly"
# 	],
# 	"monthly": [
# 		"inventory_scanner.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "inventory_scanner.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "inventory_scanner.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "inventory_scanner.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "inventory_scanner.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["inventory_scanner.utils.before_request"]
# after_request = ["inventory_scanner.utils.after_request"]

# Job Events
# ----------
# before_job = ["inventory_scanner.utils.before_job"]
# after_job = ["inventory_scanner.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"inventory_scanner.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []
