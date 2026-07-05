import frappe
from frappe.model.document import Document


class MTKBuilding(Document):
	def validate(self):
		self.validate_rate()

	def validate_rate(self):
		if self.monthly_rate_per_sqm and self.monthly_rate_per_sqm <= 0:
			frappe.throw("Monthly Rate per m² must be greater than zero.")
