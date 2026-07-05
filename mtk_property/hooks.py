app_name = "mtk_property"
app_title = "MTK Property"
app_publisher = "Yusif"
app_description = "Property Management System - Apartment & Resident Management"
app_icon = "lucide/building-2"
app_color = "#3498db"
app_version = "1.0.0"
app_license = "MIT"

# ─────────────────────────────────────────────────────────────────────
# Desk App Registration
# ─────────────────────────────────────────────────────────────────────

add_to_apps_screen = [
	{
		"name": "mtk_property",
		"logo": "/assets/mtk_property/images/mtk_icon.png",
		"title": "MTK Property",
		"route": "/app/mtk-property",
		"icon": "lucide/building-2",
		"color": "#3498db",
		"description": "Property Management - Buildings, Apartments, Residents & Bills",
	},
]

# ─────────────────────────────────────────────────────────────────────
# Includes in <head>
# ─────────────────────────────────────────────────────────────────────

app_include_css = "/assets/mtk_property/css/mtk_property.css"
app_include_js = "/assets/mtk_property/js/mtk_property.js"

# ─────────────────────────────────────────────────────────────────────
# Scheduled Tasks
# ─────────────────────────────────────────────────────────────────────

scheduler_events = {
	# Runs on the 1st of every month — auto-generates bills for all apartments
	"monthly": [
		"mtk_property.api_mtk_billing.auto_generate_monthly_bills",
	],
	# Runs every day — marks overdue bills and sends WhatsApp reminders
	"daily": [
		"mtk_property.api_mtk_billing.mark_overdue_bills",
		"mtk_property.api_mtk_billing.send_payment_reminders",
	],
}

# ─────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────

fixtures = [
	{
		"doctype": "Workspace",
		"filters": [
			["name", "=", "MTK Property"],
		],
	},
	{
		"doctype": "Number Card",
		"filters": [
			["module", "=", "MTK Property"],
		],
	},
]

# ─────────────────────────────────────────────────────────────────────
# Hooks
# ─────────────────────────────────────────────────────────────────────

after_install = "mtk_property.setup.after_install"
after_migrate = "mtk_property.setup.after_migrate"
