import frappe
from frappe.model.document import Document
from frappe.utils import flt


class MTKPayment(Document):
	def after_insert(self):
		self.mark_bill_as_paid()

	def on_cancel(self):
		self.revert_bill_status()

	def mark_bill_as_paid(self):
		if not self.bill:
			return
		bill = frappe.get_doc("MTK Monthly Bill", self.bill)
		bill.status = "Paid"
		bill.paid_amount = flt(self.amount)
		bill.payment_date = self.payment_date
		bill.flags.ignore_permissions = True
		bill.save(ignore_permissions=True)

	def revert_bill_status(self):
		if not self.bill:
			return
		bill = frappe.get_doc("MTK Monthly Bill", self.bill)
		bill.status = "Sent"
		bill.paid_amount = 0
		bill.payment_date = None
		bill.flags.ignore_permissions = True
		bill.save(ignore_permissions=True)
