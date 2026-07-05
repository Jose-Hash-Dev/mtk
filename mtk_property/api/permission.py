import frappe


def has_mtk_permission():
	"""Check if the current user can access the MTK Property module.

	Returns False when mtk_property_enabled is explicitly set to 0 in site_config.
	All logged-in users are allowed by default once MTK is enabled on the site.
	"""
	if not frappe.session.user or frappe.session.user == "Guest":
		return False
	if not frappe.conf.get("mtk_property_enabled", True):
		return False
	return True
