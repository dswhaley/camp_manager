# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Onboarding(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account_setup: DF.Check
		assigned_organization_funfangle_id: DF.Check
		assigned_organization_order_id: DF.Check
		billing_address_same: DF.Check
		camp_set_up_software: DF.Check
		care_packages_setup_if_using: DF.Check
		chose_service_package: DF.Check
		city_billing_address: DF.Data | None
		city_shipping_address: DF.Data | None
		collected_address: DF.Check
		completed_datasettings_form: DF.Check
		country_billing_address: DF.Data | None
		country_shipping_address: DF.Data | None
		downloaded_funfangle_apps: DF.Check
		exempt_status: DF.Literal["Exempt", "Taxed", "Pending"]
		first_day_of_camp: DF.Date | None
		first_day_of_camp_provided: DF.Check
		funfangle_password: DF.Data | None
		funfangle_username: DF.Data | None
		gathered_poc_information: DF.Check
		inventory_setup: DF.Check
		link_to_parent_portal: DF.Data | None
		live: DF.Check
		logobranding_recieved: DF.Check
		organization_funfangle_id: DF.Data | None
		organization_order_id: DF.Data | None
		organization_type: DF.Literal["Camp", "Other Organization"]
		poc_email: DF.Data | None
		poc_name: DF.Data | None
		poc_phone_number: DF.Data | None
		registration_identified: DF.Check
		registration_method: DF.Data | None
		registration_synced: DF.Check
		selected_features: DF.Check
		sent_retail_training_guide_if_needed: DF.Check
		set_up_admin_console: DF.Check
		set_up_parent_portal: DF.Check
		special_requirements_fulfilled: DF.Check
		state_billing_address: DF.Data | None
		state_shipping_address: DF.Data | None
		street_address_line_1_billing_address: DF.Data | None
		street_address_line_1_shipping_address: DF.Data | None
		street_address_line_2_billing_address: DF.Data | None
		street_address_line_2_shipping_address: DF.Data | None
		tax_exempt_id: DF.Data | None
		tax_exempt_id_gathered: DF.Check
		tested_parent_invitation: DF.Check
		title: DF.Data | None
		wristband_and_scanner_order: DF.Link | None
		zip_code_billing_address: DF.Data | None
		zip_code_shipping_address: DF.Data | None
	# end: auto-generated types

	pass
