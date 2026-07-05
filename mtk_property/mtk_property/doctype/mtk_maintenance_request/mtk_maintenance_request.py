import frappe
from frappe.model.document import Document
from frappe.utils import today


class MTKMaintenanceRequest(Document):
	def validate(self):
		self.set_report_date()
		self.auto_resolve()
		self.auto_assign_date()

	def set_report_date(self):
		if not self.report_date:
			self.report_date = today()

	def auto_resolve(self):
		if self.status == "Resolved" and not self.resolved_on:
			self.resolved_on = today()

	def auto_assign_date(self):
		if self.assigned_to and not self.assigned_on:
			self.assigned_on = today()
