import frappe
from frappe.model.document import Document
from frappe.utils import flt, today, getdate
from datetime import date


MONTH_MAP = {
	"January": 1, "February": 2, "March": 3, "April": 4,
	"May": 5, "June": 6, "July": 7, "August": 8,
	"September": 9, "October": 10, "November": 11, "December": 12,
}


class MTKMonthlyBill(Document):
	def validate(self):
		self.check_duplicate()
		self.set_rate_from_building()
		self.calculate_amount()
		self.set_due_date()
		self.set_title()
		self.populate_resident_info()

	def check_duplicate(self):
		existing = frappe.db.exists(
			"MTK Monthly Bill",
			{
				"apartment": self.apartment,
				"billing_month": self.billing_month,
				"billing_year": self.billing_year,
				"name": ["!=", self.name],
			},
		)
		if existing:
			frappe.throw(
				f"A bill for apartment <b>{self.apartment}</b> for "
				f"<b>{self.billing_month} {self.billing_year}</b> already exists: {existing}"
			)

	def set_rate_from_building(self):
		if self.building and not self.rate_per_sqm:
			self.rate_per_sqm = frappe.db.get_value(
				"MTK Building", self.building, "monthly_rate_per_sqm"
			) or 0

	def calculate_amount(self):
		if self.area_sqm and self.rate_per_sqm:
			self.amount = flt(self.area_sqm) * flt(self.rate_per_sqm)

	def set_due_date(self):
		if not self.due_date and self.billing_month and self.billing_year:
			month_num = MONTH_MAP.get(self.billing_month, 1)
			self.due_date = date(int(self.billing_year), month_num, 25)

	def set_title(self):
		apt_title = frappe.db.get_value("MTK Apartment", self.apartment, "title") or self.apartment
		self.title = f"{apt_title} / {self.billing_month} {self.billing_year}"

	def populate_resident_info(self):
		if self.apartment and not self.resident_name:
			resident = frappe.db.get_value(
				"MTK Resident",
				{"apartment": self.apartment, "is_active": 1},
				["full_name", "phone"],
				as_dict=True,
			)
			if resident:
				self.resident_name = resident.full_name
				self.resident_phone = resident.phone
