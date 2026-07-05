"""
MTK Billing Engine
------------------
Handles automated monthly bill generation, overdue detection,
and scheduled tasks wired via hooks.py scheduler_events.
"""

import frappe
from frappe.utils import today, getdate, nowdate
from datetime import date, datetime

MONTH_NAMES = [
	"January", "February", "March", "April", "May", "June",
	"July", "August", "September", "October", "November", "December",
]


# ─────────────────────────────────────────────────────────────────────
# Scheduled Tasks (called from hooks.py scheduler_events)
# ─────────────────────────────────────────────────────────────────────

def auto_generate_monthly_bills():
	"""
	Runs on the 1st of every month (monthly scheduler).
	Generates bills for all active apartments across all active buildings.
	"""
	today_date = getdate(today())
	month_name = MONTH_NAMES[today_date.month - 1]
	year = today_date.year

	buildings = frappe.get_all("MTK Building", filters={"status": "Active"}, pluck="name")
	total_created = 0

	for building in buildings:
		created = generate_bills_for_building(building, month_name, year)
		total_created += created

	frappe.logger().info(f"[MTK Billing] Auto-generated {total_created} bills for {month_name} {year}")


def mark_overdue_bills():
	"""
	Runs daily. Marks bills as Overdue if due_date has passed and they are still Draft or Sent.
	"""
	today_str = today()
	overdue_bills = frappe.get_all(
		"MTK Monthly Bill",
		filters={
			"status": ["in", ["Draft", "Sent"]],
			"due_date": ["<", today_str],
		},
		pluck="name",
	)

	for bill_name in overdue_bills:
		frappe.db.set_value("MTK Monthly Bill", bill_name, "status", "Overdue")

	if overdue_bills:
		frappe.db.commit()
		frappe.logger().info(f"[MTK Billing] Marked {len(overdue_bills)} bills as Overdue")


def send_payment_reminders():
	"""
	Runs daily. Sends WhatsApp reminders for bills that are Overdue
	or have been Sent but are within 5 days of the due date.
	"""
	from tensor_core.api.mtk_notifications import send_debt_reminder

	today_date = getdate(today())

	# Bills overdue or due within 5 days
	bills = frappe.get_all(
		"MTK Monthly Bill",
		filters={
			"status": ["in", ["Sent", "Overdue"]],
			"due_date": ["<=", today_date],
			"resident_phone": ["!=", ""],
		},
		fields=["name", "resident_phone", "resident_name", "amount", "billing_month", "billing_year", "apartment"],
	)

	sent = 0
	for bill in bills:
		if bill.resident_phone:
			try:
				send_debt_reminder(bill)
				sent += 1
			except Exception:
				frappe.log_error(frappe.get_traceback(), f"[MTK] Reminder failed for bill {bill.name}")

	frappe.logger().info(f"[MTK Billing] Sent {sent} payment reminders")


# ─────────────────────────────────────────────────────────────────────
# Utility Functions (callable from UI buttons / whitelisted API)
# ─────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def generate_bills_for_month(building, month_name, year):
	"""
	Whitelisted — called from the MTK Building form button.
	Generates bills for all apartments in a building for the given month/year.
	Returns a count of bills created.
	"""
	year = int(year)
	created = generate_bills_for_building(building, month_name, year)
	frappe.msgprint(
		f"Successfully generated <b>{created}</b> bill(s) for <b>{month_name} {year}</b>.",
		title="Bills Generated",
		indicator="green",
	)
	return created


def generate_bills_for_building(building, month_name, year):
	"""
	Core logic: creates MTK Monthly Bill records for all Occupied apartments
	in a building for the given month and year. Skips if bill already exists.
	"""
	rate = frappe.db.get_value("MTK Building", building, "monthly_rate_per_sqm") or 0
	apartments = frappe.get_all(
		"MTK Apartment",
		filters={"building": building, "status": "Occupied"},
		fields=["name", "area_sqm", "title"],
	)

	created = 0
	for apt in apartments:
		already_exists = frappe.db.exists(
			"MTK Monthly Bill",
			{"apartment": apt.name, "billing_month": month_name, "billing_year": year},
		)
		if already_exists:
			continue

		bill = frappe.get_doc({
			"doctype": "MTK Monthly Bill",
			"apartment": apt.name,
			"building": building,
			"billing_month": month_name,
			"billing_year": year,
			"area_sqm": apt.area_sqm,
			"rate_per_sqm": rate,
			"status": "Draft",
		})
		bill.flags.ignore_permissions = True
		bill.insert(ignore_permissions=True)
		created += 1

	frappe.db.commit()
	return created


@frappe.whitelist()
def send_bills_for_month(building, month_name, year):
	"""
	Whitelisted — marks all Draft bills for a building/month as Sent
	and triggers WhatsApp notifications to residents.
	"""
	from tensor_core.api.mtk_notifications import send_debt_reminder

	year = int(year)
	bills = frappe.get_all(
		"MTK Monthly Bill",
		filters={
			"building": building,
			"billing_month": month_name,
			"billing_year": year,
			"status": "Draft",
		},
		fields=["name", "resident_phone", "resident_name", "amount", "billing_month", "billing_year", "apartment"],
	)

	sent_count = 0
	notified_count = 0
	for bill in bills:
		frappe.db.set_value("MTK Monthly Bill", bill.name, "status", "Sent")
		sent_count += 1
		if bill.resident_phone:
			try:
				send_debt_reminder(bill)
				notified_count += 1
			except Exception:
				frappe.log_error(frappe.get_traceback(), f"[MTK] Notification failed for {bill.name}")

	frappe.db.commit()
	frappe.msgprint(
		f"Sent <b>{sent_count}</b> bills. Notified <b>{notified_count}</b> residents via WhatsApp.",
		title="Bills Sent",
		indicator="blue",
	)
	return sent_count
