import frappe
from frappe.model.document import Document
from frappe.utils import today


class MTKExpense(Document):
	def validate(self):
		if not self.expense_date:
			self.expense_date = today()
		if self.amount and self.amount <= 0:
			frappe.throw("Expense amount must be greater than zero.")
