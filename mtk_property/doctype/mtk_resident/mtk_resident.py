import frappe
from frappe.model.document import Document


class MTKResident(Document):
	def validate(self):
		self.validate_move_out()

	def validate_move_out(self):
		if self.move_out_date and self.move_in_date:
			if self.move_out_date < self.move_in_date:
				frappe.throw("Move-out Date cannot be before Move-in Date.")

		if self.move_out_date:
			# Check for outstanding unpaid bills before allowing move-out
			unpaid = frappe.db.count(
				"MTK Monthly Bill",
				{"apartment": self.apartment, "status": ["in", ["Draft", "Sent", "Overdue"]]},
			)
			if unpaid:
				frappe.msgprint(
					f"Warning: There are {unpaid} unpaid bill(s) for this apartment. "
					"Please settle all dues before the resident moves out.",
					alert=True,
					indicator="orange",
				)

	def on_update(self):
		if self.move_out_date:
			self.is_active = 0
			frappe.db.set_value("MTK Resident", self.name, "is_active", 0)
