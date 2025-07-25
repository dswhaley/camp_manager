# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class OtherOrganization(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		association: DF.Literal["", "ACA", "BSA", "CCCA", "LOM", "PCCCA", "SBC", "JCC", "OCA", "YMCA", "CCL", "AOG"]
		association_discount: DF.Data | None
		city_billing_address: DF.Data | None
		city_shipping_address: DF.Data | None
		contact_name: DF.Data | None
		contact_picture: DF.Attach | None
		country_billing_address: DF.Data | None
		country_shipping_address: DF.Data | None
		currency: DF.Link | None
		customer_and_onboarding_created: DF.Check
		email: DF.Data | None
		features: DF.Data | None
		funfangle_password: DF.Data | None
		funfangle_username: DF.Data | None
		lead_link: DF.Link | None
		link_to_parent_portal: DF.Data | None
		negotiated_regular_account: DF.Link | None
		negotiated_regular_account_price: DF.Data | None
		negotiated_staff_account: DF.Link | None
		negotiated_staff_account_price: DF.Data | None
		negotiated_wristband: DF.Link | None
		negotiated_wristband_price: DF.Data | None
		office_phone: DF.Data | None
		organization_funfangle_id: DF.Data | None
		organization_logo: DF.Attach | None
		organization_name: DF.Data
		organization_order_id: DF.Data | None
		phone: DF.Data | None
		role: DF.Data | None
		state_billing_address: DF.Data | None
		state_shipping_address: DF.Data | None
		street_address_line_1_billing_address: DF.Data | None
		street_address_line_1_shipping_address: DF.Data | None
		street_address_line_2_billing_address: DF.Data | None
		street_address_line_2_shipping_address: DF.Data | None
		tax_exempt: DF.Literal["Exempt", "Taxed", "Pending"]
		tax_exemption_number: DF.Data | None
		timezone: DF.Data | None
		website: DF.Data | None
		wristbands: DF.Data | None
		zip_code_billing_address: DF.Data | None
		zip_code_shipping_address: DF.Data | None
	# end: auto-generated types

	pass
