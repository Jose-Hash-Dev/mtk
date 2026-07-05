import frappe


# ─────────────────────────────────────────────────────────────────────
# MTK Property — Installation & Migration Hooks
# ─────────────────────────────────────────────────────────────────────

def after_install():
	"""Set up MTK Property roles and workspace when app is installed."""
	setup_mtk_roles()
	setup_mtk_number_cards()
	setup_mtk_dashboard_charts()
	setup_mtk_workspace()


def after_migrate():
	"""Sync MTK Property data after database migrations."""
	if frappe.conf.get("mtk_property_enabled", True):
		setup_mtk_roles()
		setup_mtk_number_cards()
		setup_mtk_dashboard_charts()
		setup_mtk_workspace()


# ─────────────────────────────────────────────────────────────────────
# MTK Property — Roles
# ─────────────────────────────────────────────────────────────────────

MTK_ROLES = [
	{"role_name": "MTK Admin", "desk_access": 1},
	{"role_name": "MTK Manager", "desk_access": 1},
	{"role_name": "MTK Staff", "desk_access": 1},
]


def setup_mtk_roles():
	for role_def in MTK_ROLES:
		role_name = role_def["role_name"]
		if not frappe.db.exists("Role", role_name):
			role = frappe.get_doc({"doctype": "Role", **role_def})
			role.flags.ignore_permissions = True
			role.insert(ignore_permissions=True)
	frappe.db.commit()
	print("[MTK] Roles created/verified")


# ─────────────────────────────────────────────────────────────────────
# MTK Property — Number Cards
# ─────────────────────────────────────────────────────────────────────

MTK_NUMBER_CARDS = [
	{
		"name": "MTK Total Apartments",
		"label": "Total Apartments",
		"document_type": "MTK Apartment",
		"function": "Count",
		"filters_json": "[]",
		"is_public": 1,
		"module": "MTK Property",
	},
	{
		"name": "MTK Active Residents",
		"label": "Active Residents",
		"document_type": "MTK Resident",
		"function": "Count",
		"filters_json": "[]",
		"is_public": 1,
		"module": "MTK Property",
	},
	{
		"name": "MTK Unpaid Bills",
		"label": "Unpaid Bills",
		"document_type": "MTK Monthly Bill",
		"function": "Count",
		"filters_json": "[[\"MTK Monthly Bill\", \"status\", \"=\", \"Unpaid\"]]",
		"is_public": 1,
		"module": "MTK Property",
	},
	{
		"name": "MTK Total Payments",
		"label": "Total Payments",
		"document_type": "MTK Payment",
		"function": "Count",
		"filters_json": "[]",
		"is_public": 1,
		"module": "MTK Property",
	},
]


def setup_mtk_number_cards():
	"""Create/update the four KPI Number Cards shown at the top of the MTK workspace."""
	for card_def in MTK_NUMBER_CARDS:
		# Frappe auto-generates the name from label; use label to find existing records
		existing_name = frappe.db.get_value(
			"Number Card",
			{"label": card_def["label"], "module": "MTK Property"},
			"name",
		)
		# Strip "name" so Frappe's autoname generates it on first insert
		insert_data = {k: v for k, v in card_def.items() if k != "name"}
		if existing_name:
			card = frappe.get_doc("Number Card", existing_name)
			for k, v in insert_data.items():
				setattr(card, k, v)
			card.flags.ignore_permissions = True
			card.save(ignore_permissions=True)
		else:
			card = frappe.get_doc({"doctype": "Number Card", **insert_data})
			card.flags.ignore_permissions = True
			card.insert(ignore_permissions=True)
	frappe.db.commit()
	print("[MTK] Number Cards created/updated")


# ─────────────────────────────────────────────────────────────────────
# MTK Property — Dashboard Charts
# ─────────────────────────────────────────────────────────────────────

def setup_mtk_dashboard_charts():
	"""Create the two Dashboard Charts shown in the MTK workspace."""
	charts = [
		{
			"name": "MTK Bills by Status",
			"chart_name": "MTK Bills by Status",
			"chart_type": "Group By",
			"document_type": "MTK Monthly Bill",
			"group_by_type": "Count",
			"group_by_based_on": "status",
			"type": "Pie",
			"timeseries": 0,
			"filters_json": "[]",
			"is_public": 1,
			"module": "MTK Property",
		},
		{
			"name": "MTK Residents Over Time",
			"chart_name": "MTK Residents Over Time",
			"chart_type": "Count",
			"document_type": "MTK Resident",
			"based_on": "creation",
			"type": "Bar",
			"timeseries": 1,
			"time_interval": "Monthly",
			"timespan": "Last Year",
			"filters_json": "[]",
			"is_public": 1,
			"module": "MTK Property",
		},
	]
	for chart_def in charts:
		existing_name = frappe.db.get_value(
			"Dashboard Chart",
			{"chart_name": chart_def["chart_name"], "module": "MTK Property"},
			"name",
		)
		insert_data = {k: v for k, v in chart_def.items() if k != "name"}
		if existing_name:
			chart = frappe.get_doc("Dashboard Chart", existing_name)
			for k, v in insert_data.items():
				setattr(chart, k, v)
			chart.flags.ignore_permissions = True
			chart.save(ignore_permissions=True)
		else:
			chart = frappe.get_doc({"doctype": "Dashboard Chart", **insert_data})
			chart.flags.ignore_permissions = True
			chart.insert(ignore_permissions=True)
	frappe.db.commit()
	print("[MTK] Dashboard Charts created/updated")


# ─────────────────────────────────────────────────────────────────────
# MTK Property — Workspace
# ─────────────────────────────────────────────────────────────────────

MTK_WORKSPACE_CONTENT = [
	# ── Dashboard header ──────────────────────────────────────────────
	{
		"type": "header",
		"data": {
			"text": "<span class=\"h4\"><b>MTK Property Management</b></span>",
			"col": 12,
		},
	},
	# ── KPI number cards ─────────────────────────────────────────────
	{
		"type": "number_card",
		"data": {"number_card_name": "Total Apartments", "col": 3},
	},
	{
		"type": "number_card",
		"data": {"number_card_name": "Active Residents", "col": 3},
	},
	{
		"type": "number_card",
		"data": {"number_card_name": "Unpaid Bills", "col": 3},
	},
	{
		"type": "number_card",
		"data": {"number_card_name": "Total Payments", "col": 3},
	},
	# ── Charts ───────────────────────────────────────────────────────
	{
		"type": "header",
		"data": {
			"text": "<span class=\"h6\"><b>Trends</b></span>",
			"col": 12,
		},
	},
	{
		"type": "chart",
		"data": {"chart_name": "MTK Bills by Status", "col": 6},
	},
	{
		"type": "chart",
		"data": {"chart_name": "MTK Residents Over Time", "col": 6},
	},
	# ── Quick-access shortcuts ────────────────────────────────────────
	{
		"type": "header",
		"data": {
			"text": "<span class=\"h6\"><b>Quick Access</b></span>",
			"col": 12,
		},
	},
	{
		"type": "shortcut",
		"data": {
			"shortcut_name": "MTK Building",
			"col": 3,
			"color": "Blue",
			"format": "{} Building(s)",
			"icon": "lucide/building-2",
			"label": "Buildings",
			"link_to": "MTK Building",
			"type": "DocType",
		},
	},
	{
		"type": "shortcut",
		"data": {
			"shortcut_name": "MTK Apartment",
			"col": 3,
			"color": "Green",
			"format": "{} Apartment(s)",
			"icon": "lucide/home",
			"label": "Apartments",
			"link_to": "MTK Apartment",
			"type": "DocType",
		},
	},
	{
		"type": "shortcut",
		"data": {
			"shortcut_name": "MTK Resident",
			"col": 3,
			"color": "Purple",
			"format": "{} Resident(s)",
			"icon": "lucide/users",
			"label": "Residents",
			"link_to": "MTK Resident",
			"type": "DocType",
		},
	},
	{
		"type": "shortcut",
		"data": {
			"shortcut_name": "MTK Monthly Bill",
			"col": 3,
			"color": "Orange",
			"format": "{} Bill(s)",
			"icon": "lucide/file-text",
			"label": "Bills",
			"link_to": "MTK Monthly Bill",
			"type": "DocType",
		},
	},
	{
		"type": "shortcut",
		"data": {
			"shortcut_name": "MTK Payment",
			"col": 3,
			"color": "Green",
			"format": "{} Payment(s)",
			"icon": "lucide/credit-card",
			"label": "Payments",
			"link_to": "MTK Payment",
			"type": "DocType",
		},
	},
	{
		"type": "shortcut",
		"data": {
			"shortcut_name": "MTK Maintenance Request",
			"col": 3,
			"color": "Red",
			"format": "{} Request(s)",
			"icon": "lucide/wrench",
			"label": "Maintenance",
			"link_to": "MTK Maintenance Request",
			"type": "DocType",
		},
	},
	{
		"type": "shortcut",
		"data": {
			"shortcut_name": "MTK Expense",
			"col": 3,
			"color": "Yellow",
			"format": "{} Expense(s)",
			"icon": "lucide/wallet",
			"label": "Expenses",
			"link_to": "MTK Expense",
			"type": "DocType",
		},
	},
]


def setup_mtk_workspace():
	import json

	workspace_name = "MTK Property"
	shortcut_rows = [
		{
			"doctype": "Workspace Shortcut",
			"label": s["data"]["label"],
			"link_to": s["data"]["link_to"],
			"type": s["data"]["type"],
			"color": s["data"].get("color", "Blue"),
			"icon": s["data"].get("icon", ""),
		}
		for s in MTK_WORKSPACE_CONTENT
		if s.get("type") == "shortcut"
	]

	workspace_data = {
		"doctype": "Workspace",
		"name": workspace_name,
		"title": "MTK Property",
		"module": "MTK Property",
		"label": "MTK Property",
		"is_standard": 1,
		"public": 1,
		"icon": "lucide/building-2",
		"indicator_color": "green",
		"content": json.dumps(MTK_WORKSPACE_CONTENT),
		"shortcuts": shortcut_rows,
	}

	if frappe.db.exists("Workspace", workspace_name):
		ws = frappe.get_doc("Workspace", workspace_name)
		ws.content = workspace_data["content"]
		ws.icon = workspace_data["icon"]
		ws.indicator_color = workspace_data["indicator_color"]
		ws.is_standard = 1
		ws.set("shortcuts", shortcut_rows)
		ws.flags.ignore_permissions = True
		ws.flags.ignore_links = True
		ws.save(ignore_permissions=True)
	else:
		ws = frappe.get_doc(workspace_data)
		ws.flags.ignore_permissions = True
		ws.flags.ignore_links = True
		ws.insert(ignore_permissions=True)

	frappe.db.commit()

	# Always ensure Desktop Icon has a valid link
	_fix_mtk_desktop_icon(workspace_name)
	print("[MTK] Workspace created/updated")


def _fix_mtk_desktop_icon(workspace_name: str):
	"""Ensure the Desktop Icon for the MTK workspace always has the correct type and link."""
	workspace_slug = workspace_name.lower().replace(" ", "-")
	correct_link = f"/app/{workspace_slug}"

	# Always set icon_type=Link and link_type=Workspace Sidebar so clicking
	# the tile navigates properly instead of showing "Icon not configured"
	frappe.db.sql(
		"""
		UPDATE `tabDesktop Icon`
		SET icon_type  = 'Link',
		    link_type  = 'Workspace Sidebar',
		    link       = %s,
		    icon_image = NULL,
		    modified   = NOW()
		WHERE label = %s
		""",
		(correct_link, workspace_name),
	)
	# Fix any other workspace sidebar icons that lost their link after migrate
	frappe.db.sql(
		"""
		UPDATE `tabDesktop Icon`
		SET link = CONCAT('/app/', LOWER(REPLACE(REPLACE(label, ' ', '-'), '_', '-'))),
		    modified = NOW()
		WHERE link_type = 'Workspace Sidebar'
		  AND (link IS NULL OR link = '')
		""",
	)
	frappe.db.commit()
