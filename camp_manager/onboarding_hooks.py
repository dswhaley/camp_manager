
# Import Frappe for ERPNext document and database operations
import frappe
# JSON and OS are available for config/file operations if needed
import json
import os
# Time is imported for any future timing or delay logic
import time


def manage_onboarding(doc, method):
    """
    Main entry point for onboarding management logic.
    This function updates the onboarding phase and synchronizes data between the onboarding document
    and the linked Camp or Other Organization document, depending on the organization_type.
    Args:
        doc: The onboarding document being processed.
        method: The method triggering the hook (e.g., before_save).
    """
    update_phase(doc)  # Update the onboarding phase based on completed steps
    if doc.organization_type == "Camp":
        update_camp(doc)  # Sync onboarding info to linked Camp document
    else:
        update_organization(doc)  # Sync onboarding info to linked Other Organization document


def update_phase(doc):
    """
    Determines and sets the current onboarding phase based on which onboarding steps have been completed.
    The phase is incremented as more steps are completed, and is set to 'Live' when the organization is live.
    Args:
        doc: The onboarding document being processed.
    """
    phase = "1"  # Default phase is 1 (initial onboarding)
    # Phase 2: Registration, tax, and first day info gathered
    if (doc.chose_service_package and doc.selected_features and doc.registration_identified and
        doc.tax_exempt_id_gathered and doc.first_day_of_camp_provided):
        phase = "2"
    # Phase 3: Address, POC, account setup, IDs, portal, admin, training, discount
    if (doc.collected_address and doc.gathered_poc_information and doc.account_setup and
        doc.assigned_organization_order_id and doc.assigned_organization_funfangle_id and doc.set_up_parent_portal and 
        doc.set_up_admin_console and doc.sent_retail_training_guide_if_needed and doc.custom_set_discount):
        phase = "3"
    # Phase 4: Data settings, apps, software, branding
    if (doc.completed_datasettings_form and doc.downloaded_funfangle_apps and
        doc.camp_set_up_software and doc.logobranding_recieved):
        phase = "4"
    # Phase 5: Wristband/scanner order or marked as not applicable
    if (doc.wristband_and_scanner_order or doc.custom_order_na):
        phase = "5"
    # Phase 6: Inventory and care packages setup
    if (doc.inventory_setup and doc.care_packages_setup_if_using):
        phase = "6"
    # Phase 7: Registration synced and special requirements fulfilled
    if (doc.registration_synced and doc.special_requirements_fulfilled):
        phase = "7"
    # Phase 8: Parent invitation tested
    if doc.tested_parent_invitation:
        phase = "8"
    # Final phase: Organization is live
    if doc.live:
        phase = "Live"
    # Set the custom_phase field to the determined phase
    doc.custom_phase = phase


def update_camp(doc):
    """
    Synchronizes onboarding information to the linked Camp document.
    This function updates the Camp record with the latest onboarding data, ensuring that all relevant fields
    (registration, tax, address, POC, account setup, IDs, etc.) are kept in sync. This is critical for downstream
    processes and reporting accuracy.
    Args:
        doc: The onboarding document being processed.
    """
    try:
        # Skip update for new onboarding documents
        if doc.is_new():
            return
        # Retrieve the original onboarding document for comparison
        if not hasattr(doc, "_original"):
            doc._original = frappe.get_doc(doc.doctype, doc.name)

        original = doc._original
        try:
            # Only update if a linked Camp exists
            if frappe.db.exists("Camp", {"name": doc.title}):            
                camp = frappe.get_doc("Camp", doc.title)

            # Registration Method: Sync registration software field
            if camp.registration_software != doc.registration_method and doc.registration_method:
                camp.registration_software = doc.registration_method
            if camp.registration_software:
                doc.registration_identified = 1  # Mark registration as identified

            # Tax Info: Sync exemption status and ID
            if camp.tax_exempt != doc.exempt_status and doc.exempt_status != "Pending":
                camp.tax_exempt = doc.exempt_status
            if camp.tax_exemption_number != doc.tax_exempt_id:
                camp.tax_exemption_number = doc.tax_exempt_id
            if camp.tax_exempt == "Taxed" or (camp.tax_exempt == "Exempt" and camp.tax_exemption_number):
                doc.tax_exempt_id_gathered = 1  # Mark tax info as gathered

            # First Day of Camp: Sync first day field
            if camp.first_day_of_camp != doc.first_day_of_camp and doc.first_day_of_camp:
                camp.first_day_of_camp = doc.first_day_of_camp
            if camp.first_day_of_camp:
                doc.first_day_of_camp_provided = 1  # Mark first day as provided

            # Discount/Association: Sync association field
            if camp.association != doc.custom_discount and doc.custom_discount:
                camp.association = doc.custom_discount
            if camp.association:
                doc.custom_set_discount = 1  # Mark discount as set

            # Shipping Address: Sync all address fields if changed
            if original.street_address_line_1_shipping_address != doc.street_address_line_1_shipping_address:
                camp.street_address_line_1_shipping_address = doc.street_address_line_1_shipping_address
            if original.street_address_line_2_shipping_address != doc.street_address_line_2_shipping_address:
                camp.street_address_line_2_shipping_address = doc.street_address_line_2_shipping_address
            if original.city_shipping_address != doc.city_shipping_address:
                camp.city_shipping_address = doc.city_shipping_address
            if original.state_shipping_address != doc.state_shipping_address:
                camp.state_shipping_address = doc.state_shipping_address
            if original.zip_code_shipping_address != doc.zip_code_shipping_address:
                camp.zip_code_shipping_address = doc.zip_code_shipping_address
            if original.country_shipping_address != doc.country_shipping_address:
                camp.country_shipping_address = doc.country_shipping_address

            # Billing Address: Sync all billing address fields if changed
            if original.street_address_line_1_billing_address != doc.street_address_line_1_billing_address:
                camp.street_address_line_1_billing_address = doc.street_address_line_1_billing_address
            if original.street_address_line_2_billing_address != doc.street_address_line_2_billing_address:
                camp.street_address_line_2_billing_address = doc.street_address_line_2_billing_address
            if original.city_billing_address != doc.city_billing_address:
                camp.city_billing_address = doc.city_billing_address
            if original.state_billing_address != doc.state_billing_address:
                camp.state_billing_address = doc.state_billing_address
            if original.zip_code_billing_address != doc.zip_code_billing_address:
                camp.zip_code_billing_address = doc.zip_code_billing_address
            if original.country_billing_address != doc.country_billing_address:
                camp.country_billing_address = doc.country_billing_address

            # If all required address fields are present, mark address as collected
            if (
                doc.street_address_line_1_shipping_address and
                doc.street_address_line_2_shipping_address and
                doc.city_shipping_address and
                doc.state_shipping_address and
                doc.zip_code_shipping_address and
                doc.country_shipping_address and
                (
                    doc.billing_address_same or (
                        doc.street_address_line_1_billing_address and
                        doc.street_address_line_2_billing_address and
                        doc.city_billing_address and
                        doc.state_billing_address and
                        doc.zip_code_billing_address and
                        doc.country_billing_address
                    )
                )
            ):
                doc.collected_address = 1

            # POC Info: Sync point-of-contact fields
            if camp.contact_name != doc.poc_name and doc.poc_name:
                camp.contact_name = doc.poc_name
            if camp.email != doc.poc_email and doc.poc_email:
                camp.email = doc.poc_email
            if camp.phone != doc.poc_phone_number and doc.poc_phone_number:
                camp.phone = doc.poc_phone_number
            if camp.contact_name and camp.email and camp.phone:
                doc.gathered_poc_information = 1  # Mark POC info as gathered

            # Account Setup: Sync Funfangle credentials
            if camp.funfangle_username != doc.funfangle_username and doc.funfangle_username:
                camp.funfangle_username = doc.funfangle_username
            if camp.funfangle_password != doc.funfangle_password and doc.funfangle_password:
                camp.funfangle_password = doc.funfangle_password
            if camp.funfangle_password and camp.funfangle_username:
                doc.account_setup = 1  # Mark account setup as complete

            # Parent Portal: Sync portal link
            if camp.link_to_parent_portal != doc.link_to_parent_portal and doc.link_to_parent_portal:
                camp.link_to_parent_portal = doc.link_to_parent_portal
            if camp.link_to_parent_portal:
                doc.set_up_parent_portal = 1  # Mark portal setup as complete

            # Organization IDs: Sync order and Funfangle IDs
            if camp.organization_order_id != doc.organization_order_id and doc.organization_order_id:
                camp.organization_order_id = doc.organization_order_id
            if camp.organization_order_id:
                doc.assigned_organization_order_id = 1  # Mark order ID as assigned

            if camp.organization_funfangle_id != doc.organization_funfangle_id and doc.organization_funfangle_id:
                camp.organization_funfangle_id = doc.organization_funfangle_id
            if camp.organization_funfangle_id:
                doc.assigned_organization_funfangle_id = 1  # Mark Funfangle ID as assigned

            camp.save(ignore_permissions=True)  # Save all changes to Camp document

        except frappe.DoesNotExistError:
            # If linked Camp does not exist, throw error for user
            frappe.throw(f"Linked Camp '{doc.title}' not found.")

    except Exception as e:
        # Log and notify user of any errors during update
        frappe.msgprint(f"❌ Failed to update the Camp information for {doc.name}: {str(e)}")
        frappe.log_error(f"❌ Error updating Camp in Onboarding for {doc.name}: {str(e)}", "manage_onboarding error")


def update_organization(doc):
    """
    Synchronizes onboarding information to the linked Other Organization document.
    This function updates the Other Organization record with the latest onboarding data, ensuring that all relevant fields
    (tax, address, POC, account setup, IDs, etc.) are kept in sync. This is critical for downstream processes and reporting accuracy.
    Args:
        doc: The onboarding document being processed.
    """
    try:
        # Skip update for new onboarding documents
        if doc.is_new():
            return
        # Retrieve the original onboarding document for comparison
        if not hasattr(doc, "_original"):
            doc._original = frappe.get_doc(doc.doctype, doc.name)

        original = doc._original
        try:
            # Only update if a linked Other Organization exists
            if frappe.db.exists("Other Organization", {"name": doc.title}):  # Corrected DocType
                other_organization = frappe.get_doc("Other Organization", doc.title)

            # Tax Info: Sync exemption status and ID
            if original.exempt_status != doc.exempt_status and doc.exempt_status != "Pending":
                other_organization.tax_exempt = doc.exempt_status
            if original.tax_exempt_id != doc.tax_exempt_id and doc.tax_exempt_id:
                other_organization.tax_exemption_number = doc.tax_exempt_id
            if other_organization.tax_exempt == "Taxed" or (other_organization.tax_exempt and other_organization.tax_exemption_number):
                doc.tax_exempt_id_gathered = 1  # Mark tax info as gathered

            # Discount/Association: Sync association field
            if original.custom_discount != doc.custom_discount and doc.custom_discount:
                other_organization.association = doc.custom_discount
            if other_organization.association:
                doc.custom_set_discount = 1  # Mark discount as set

            # Shipping Address: Sync all address fields if changed
            if original.street_address_line_1_shipping_address != doc.street_address_line_1_shipping_address:
                other_organization.street_address_line_1_shipping_address = doc.street_address_line_1_shipping_address
            if original.street_address_line_2_shipping_address != doc.street_address_line_2_shipping_address:
                other_organization.street_address_line_2_shipping_address = doc.street_address_line_2_shipping_address
            if original.city_shipping_address != doc.city_shipping_address:
                other_organization.city_shipping_address = doc.city_shipping_address
            if original.state_shipping_address != doc.state_shipping_address:
                other_organization.state_shipping_address = doc.state_shipping_address
            if original.zip_code_shipping_address != doc.zip_code_shipping_address:
                other_organization.zip_code_shipping_address = doc.zip_code_shipping_address
            if original.country_shipping_address != doc.country_shipping_address:
                other_organization.country_shipping_address = doc.country_shipping_address

            # Billing Address: Sync all billing address fields if changed
            if original.street_address_line_1_billing_address != doc.street_address_line_1_billing_address:
                other_organization.street_address_line_1_billing_address = doc.street_address_line_1_billing_address
            if original.street_address_line_2_billing_address != doc.street_address_line_2_billing_address:
                other_organization.street_address_line_2_billing_address = doc.street_address_line_2_billing_address
            if original.city_billing_address != doc.city_billing_address:
                other_organization.city_billing_address = doc.city_billing_address
            if original.state_billing_address != doc.state_billing_address:
                other_organization.state_billing_address = doc.state_billing_address
            if original.zip_code_billing_address != doc.zip_code_billing_address:
                other_organization.zip_code_billing_address = doc.zip_code_billing_address
            if original.country_billing_address != doc.country_billing_address:
                other_organization.country_billing_address = doc.country_billing_address

            # If all required address fields are present, mark address as collected
            if (
                doc.street_address_line_1_shipping_address and
                doc.city_shipping_address and
                doc.state_shipping_address and
                doc.zip_code_shipping_address and
                doc.country_shipping_address and
                (
                    doc.billing_address_same or (
                        doc.street_address_line_1_billing_address and
                        doc.city_billing_address and
                        doc.state_billing_address and
                        doc.zip_code_billing_address and
                        doc.country_billing_address
                    )
                )
            ):
                doc.collected_address = 1

            # POC Info: Sync point-of-contact fields
            if original.poc_name != doc.poc_name and doc.poc_name:
                other_organization.contact_name = doc.poc_name
            if original.poc_email != doc.poc_email and doc.poc_email:
                other_organization.email = doc.poc_email
            if original.poc_phone_number != doc.poc_phone_number and doc.poc_phone_number:
                other_organization.phone = doc.poc_phone_number
            if other_organization.contact_name and other_organization.email and other_organization.phone:
                doc.gathered_poc_information = 1  # Mark POC info as gathered

            # Organization IDs: Sync order and Funfangle IDs
            if original.organization_order_id != doc.organization_order_id and doc.organization_order_id:
                other_organization.organization_order_id = doc.organization_order_id
            if other_organization.organization_order_id:
                doc.assigned_organization_order_id = 1  # Mark order ID as assigned

            if original.organization_funfangle_id != doc.organization_funfangle_id and doc.organization_funfangle_id:
                other_organization.organization_funfangle_id = doc.organization_funfangle_id
            if other_organization.organization_funfangle_id:
                doc.assigned_organization_funfangle_id = 1  # Mark Funfangle ID as assigned

            # Account Setup: Sync Funfangle credentials
            if other_organization.funfangle_username != doc.funfangle_username and doc.funfangle_username:
                other_organization.funfangle_username = doc.funfangle_username
            if other_organization.funfangle_password != doc.funfangle_password and doc.funfangle_password:
                other_organization.funfangle_password = doc.funfangle_password
            if other_organization.funfangle_password and other_organization.funfangle_username:
                doc.account_setup = 1  # Mark account setup as complete

            # Parent Portal: Sync portal link
            if other_organization.link_to_parent_portal != doc.link_to_parent_portal and doc.link_to_parent_portal:
                other_organization.link_to_parent_portal = doc.link_to_parent_portal
            if other_organization.link_to_parent_portal:
                doc.set_up_parent_portal = 1  # Mark portal setup as complete
            other_organization.save(ignore_permissions=True)  # Save all changes to Other Organization document

        except frappe.DoesNotExistError:
            # If linked Other Organization does not exist, throw error for user
            frappe.throw(f"Linked Other Organization '{doc.title}' not found.")

    except Exception as e:
        # Log and notify user of any errors during update
        frappe.msgprint(f"❌ Failed to update the Other Organization information for {doc.name}")
        frappe.log_error(f"❌ Error updating Other Organization in Onboarding for {doc.name}: {str(e)}", "manage_onboarding error")

        