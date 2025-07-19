import frappe
import json
import os
import time

def manage_onboarding(doc, method):
    update_phase(doc)
    if doc.organization_type == "Camp":
        update_camp(doc)
    else:
        update_organization(doc)

def update_phase(doc):
    phase = "1"
    if (doc.chose_service_package and doc.selected_features and doc.registration_identified and
        doc.tax_exempt_id_gathered and doc.first_day_of_camp_provided):
        phase = "2"
    if (doc.collected_address and doc.gathered_poc_information and doc.account_setup and
        doc.assigned_organization_order_id and doc.assigned_organization_funfangle_id and doc.set_up_parent_portal and 
        doc.set_up_admin_console and doc.sent_retail_training_guide_if_needed and doc.custom_set_discount):
        phase = "3"
    if (doc.completed_datasettings_form and doc.downloaded_funfangle_apps and
        doc.camp_set_up_software and doc.logobranding_recieved):
        phase = "4"
    if (doc.wristband_and_scanner_order or doc.custom_order_na):
        phase = "5"
    if (doc.inventory_setup and doc.care_packages_setup_if_using):
        phase = "6"
    if (doc.registration_synced and doc.special_requirements_fulfilled):
        phase = "7"
    if doc.tested_parent_invitation:
        phase = "8"
    if doc.live:
        phase = "Live"
    
    doc.custom_phase = phase

def update_camp(doc):
    try:
        if doc.is_new():
            return
        if not hasattr(doc, "_original"):
            doc._original = frappe.get_doc(doc.doctype, doc.name)

        original = doc._original
        try:
            if frappe.db.exists("Camp", {"name": doc.title}):            
                camp = frappe.get_doc("Camp", doc.title)

            # Registration Method
            if camp.registration_software != doc.registration_method and doc.registration_method:
                camp.registration_software = doc.registration_method
            if camp.registration_software:
                doc.registration_identified = 1

            # Tax Info
            if camp.tax_exempt != doc.exempt_status and doc.exempt_status != "Pending":
                camp.tax_exempt = doc.exempt_status
            if camp.tax_exemption_number != doc.tax_exempt_id:
                camp.tax_exemption_number = doc.tax_exempt_id
            if camp.tax_exempt == "Taxed" or (camp.exempt_status == "Exempt" and camp.tax_exemption_number):
                doc.tax_exempt_id_gathered = 1

            # First Day of Camp
            if camp.first_day_of_camp != doc.first_day_of_camp and doc.first_day_of_camp:
                camp.first_day_of_camp = doc.first_day_of_camp
            if camp.first_day_of_camp:
                doc.first_day_of_camp_provided = 1

            if camp.association != doc.custom_discount and doc.custom_discount:
                camp.association = doc.custom_discount
            if camp.association:
                doc.custom_set_discount = 1

            # Shipping Address
            if camp.shipping_address_1 != doc.shipping_address_1:
                camp.shipping_address_1 = doc.shipping_address_1
            if camp.shipping_address_2 != doc.shipping_address_2:
                camp.shipping_address_2 = doc.shipping_address_2
            if camp.shipping_address_3 != doc.shipping_address_3:
                camp.shipping_address_3 = doc.shipping_address_3
                update_currency(doc, camp)

            # Billing Address
            if camp.billing_address_1 != doc.billing_address_1:
                camp.billing_address_1 = doc.billing_address_1
            if camp.billing_address_2 != doc.billing_address_2:
                camp.billing_address_2 = doc.billing_address_2
            if camp.billing_address_3 != doc.billing_address_3:
                camp.billing_address_3 = doc.billing_address_3

            # Collected Address Flag
            if ((doc.shipping_address_1 and doc.shipping_address_2) and
                (doc.billing_address_1 and doc.billing_address_2 or doc.billing_address_same)):
                doc.collected_address = 1

            # POC Info
            if camp.contact_name != doc.poc_name and doc.poc_name:
                camp.contact_name = doc.poc_name
            if camp.email != doc.poc_email and doc.poc_email:
                camp.email = doc.poc_email
            if camp.phone != doc.poc_phone_number and doc.poc_phone_number:
                camp.phone = doc.poc_phone_number
            if camp.contact_name and camp.email and camp.phone:
                doc.gathered_poc_information = 1

            if camp.funfangle_username != doc.funfangle_username and doc.funfangle_username:
                camp.funfangle_username = doc.funfangle_username
            if camp.funfangle_password != doc.funfangle_password and doc.funfangle_password:
                camp.funfangle_password = doc.funfangle_password
            if camp.funfangle_password and camp.funfangle_username:
                doc.account_setup = 1
            

            if camp.link_to_parent_portal != doc.link_to_parent_portal and doc.link_to_parent_portal:
                camp.link_to_parent_portal = doc.link_to_parent_portal
            if camp.link_to_parent_portal:
                doc.set_up_parent_portal = 1

            # Organization ID
            if camp.organization_order_id != doc.organization_order_id and doc.organization_order_id:
                camp.organization_order_id = doc.organization_order_id
            if camp.organization_order_id:
                doc.assigned_organization_order_id = 1

            if camp.organization_funfangle_id != doc.organization_funfangle_id and doc.organization_funfangle_id:
                camp.organization_funfangle_id = doc.organization_funfangle_id
            if camp.organization_funfangle_id:
                doc.assigned_organization_funfangle_id = 1

            camp.save(ignore_permissions=True)

            # if doc.shipping_address_1 and doc.shipping_address_2 and doc.exempt_status != "Pending" and doc.poc_email and doc.poc_phone_number:
            #     if (doc.exempt_status == "Exempt" and doc.tax_exempt_id) or doc.exempt_status == "Taxed":
            #         cust = frappe.get_doc("Customer", doc.name)
            #         print("About to enqueue")
            #         #cust.custom_create_customer_in_qbo = 1
            #         frappe.enqueue("camp_manager.utils.sync_customer", queue='default', customer=cust.name)


        except frappe.DoesNotExistError:
            frappe.throw(f"Linked Camp '{doc.title}' not found.")

    except Exception as e:
        frappe.msgprint(f"❌ Failed to update the Camp information for {doc.name}: {str(e)}")
        frappe.log_error(f"❌ Error updating Camp in Onboarding for {doc.name}: {str(e)}", "manage_onboarding error")
def sync_customer(customer):
    print("Running")
    cust = frappe.get_doc("Customer", customer)
    cust.custom_create_customer_in_qbo
    cust.save(ignore_permissions=True)
def update_organization(doc):
    try:
        if doc.is_new():
            return
        if not hasattr(doc, "_original"):
            doc._original = frappe.get_doc(doc.doctype, doc.name)

        original = doc._original
        try:
            if frappe.db.exists("Other Organization", {"name": doc.title}):  # Corrected DocType
                other_organization = frappe.get_doc("Other Organization", doc.title)

            # Tax Info
            if original.exempt_status != doc.exempt_status and doc.exempt_status != "Pending":
                other_organization.tax_exempt = doc.exempt_status
            if original.tax_exempt_id != doc.tax_exempt_id and doc.tax_exempt_id:
                other_organization.tax_exemption_number = doc.tax_exempt_id
            if other_organization.tax_exempt == "Taxed" or (other_organization.tax_exempt and other_organization.tax_exemption_number):
                doc.tax_exempt_id_gathered = 1

            if original.custom_discount != doc.custom_discount and doc.custom_discount:
                other_organization.association = doc.custom_discount
            if other_organization.association:
                doc.custom_set_discount = 1

            # Shipping Address
            if original.shipping_address_1 != doc.shipping_address_1:
                other_organization.shipping_address_1 = doc.shipping_address_1
            if original.shipping_address_2 != doc.shipping_address_2:
                other_organization.shipping_address_2 = doc.shipping_address_2
            if original.shipping_address_3 != doc.shipping_address_3:
                other_organization.shipping_address_3 = doc.shipping_address_3
                update_currency(doc, other_organization)

            # Billing Address
            if original.billing_address_1 != doc.billing_address_1:
                other_organization.billing_address_1 = doc.billing_address_1
            if original.billing_address_2 != doc.billing_address_2:
                other_organization.billing_address_2 = doc.billing_address_2
            if original.billing_address_3 != doc.billing_address_3:
                other_organization.billing_address_3 = doc.billing_address_3

            
            # Collected Address Flag
            if ((doc.shipping_address_1 and doc.shipping_address_2) and
                (doc.billing_address_1 and doc.billing_address_2 or doc.billing_address_same)):
                doc.collected_address = 1

            # POC Info
            if original.poc_name != doc.poc_name and doc.poc_name:
                other_organization.contact_name = doc.poc_name
            if original.poc_email != doc.poc_email and doc.poc_email:
                other_organization.email = doc.poc_email
            if original.poc_phone_number != doc.poc_phone_number and doc.poc_phone_number:
                other_organization.phone = doc.poc_phone_number
            if other_organization.contact_name and other_organization.email and other_organization.phone:
                doc.gathered_poc_information = 1

            # Organization ID
            if original.organization_order_id != doc.organization_order_id and doc.organization_order_id:
                other_organization.organization_order_id = doc.organization_order_id
            if other_organization.organization_order_id:
                doc.assigned_organization_order_id = 1

            if original.organization_funfangle_id != doc.organization_funfangle_id and doc.organization_funfangle_id:
                other_organization.organization_funfangle_id = doc.organization_funfangle_id
            if other_organization.organization_funfangle_id:
                doc.assigned_organization_funfangle_id = 1

            if other_organization.funfangle_username != doc.funfangle_username and doc.funfangle_username:
                other_organization.funfangle_username = doc.funfangle_username
            if other_organization.funfangle_password != doc.funfangle_password and doc.funfangle_password:
                other_organization.funfangle_password = doc.funfangle_password
            if other_organization.funfangle_password and other_organization.funfangle_username:
                doc.account_setup = 1
            

            if other_organization.link_to_parent_portal != doc.link_to_parent_portal and doc.link_to_parent_portal:
                other_organization.link_to_parent_portal = doc.link_to_parent_portal
            if other_organization.link_to_parent_portal:
                doc.set_up_parent_portal = 1
            other_organization.save(ignore_permissions=True)

            # if doc.shipping_address_1 and doc.shipping_address_2 and doc.exempt_status != "Pending" and doc.poc_email and doc.poc_phone_number:
            #     if (doc.exempt_status == "Exempt" and doc.tax_exempt_id) or doc.exempt_status == "Taxed":
            #         cust = frappe.get_doc("Customer", doc.name)
            #         print("About to enqueue")
            #         #cust.custom_create_customer_in_qbo = 1
            #         frappe.enqueue("camp_manager.utils.sync_customer", queue='default', customer=cust.name)

        except frappe.DoesNotExistError:
            frappe.throw(f"Linked Other Organization '{doc.title}' not found.")

    except Exception as e:
        frappe.msgprint(f"❌ Failed to update the Other Organization information for {doc.name}")
        frappe.log_error(f"❌ Error updating Other Organization in Onboarding for {doc.name}: {str(e)}", "manage_onboarding error")

def update_currency(doc, org):
    print("***************************WE GOT HERE")
    file_path = os.path.join(os.path.dirname(__file__), "country_currency_map.json")
    with open(file_path, "r") as file:
        country_currency = json.load(file)
        country = doc.shipping_address_3.lower()
        currency = country_currency.get(country.lower())
        print(f"********************************Currency is: {currency}")
        if currency:
            org.currency = currency
        else:
            org.currency = "USD"        