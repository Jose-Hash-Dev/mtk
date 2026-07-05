import frappe
from frappe.model.document import Document
from frappe.utils import flt


class MTKApartment(Document):
	def validate(self):
		self.set_title()
		self.calculate_monthly_amount()

	def set_title(self):
		block_name = frappe.db.get_value("MTK Block", self.block, "block_name") if self.block else ""
		self.title = f"{block_name} - Apt {self.apartment_number}"

	def calculate_monthly_amount(self):
		if self.area_sqm and self.building:
			rate = frappe.db.get_value("MTK Building", self.building, "monthly_rate_per_sqm") or 0
			self.monthly_amount = flt(self.area_sqm) * flt(rate)
		else:
			self.monthly_amount = 0
