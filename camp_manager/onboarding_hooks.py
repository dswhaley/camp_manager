import frappe

def manage_onboarding(doc, method):
    update_phase(doc)
    update_camp(doc)

def update_phase(doc):
    phase = "1"
    if (doc.camp_chose_service_package and doc.camp_selected_features and doc.registration_identified and
        doc.tax_exempt_id_gathered and doc.first_day_of_camp_provided):
        phase = "2"
    if (doc.collected_address and doc.gathered_poc_information and doc.account_setup and
        doc.assigned_organization_id and doc.set_up_parent_portal and 
        doc.set_up_admin_console and doc.sent_retail_training_guide_if_needed and doc.custom_set_discount):
        phase = "3"
    if (doc.camp_completed_datasettings_form and doc.camp_downloaded_funfangle_apps and
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
        if not hasattr(doc, "_original"):
            doc._original = frappe.get_doc(doc.doctype, doc.name)

        original = doc._original

        try:
            camp = frappe.get_doc("Camp", doc.custom_camp_link)

            # Registration Method
            if original.registration_method != doc.registration_method and doc.registration_method:
                camp.registration_software = doc.registration_method
                doc.registration_identified = 1

            # Tax Info
            if original.exempt_status != doc.exempt_status:
                camp.tax_exempt = doc.exempt_status
            if original.tax_exempt_id != doc.tax_exempt_id:
                camp.tax_exemption_number = doc.tax_exempt_id
            if doc.exempt_status == "Taxed" or (doc.exempt_status and doc.tax_exempt_id):
                doc.tax_exempt_id_gathered = 1

            # First Day of Camp
            if original.first_day_of_camp != doc.first_day_of_camp and doc.first_day_of_camp:
                camp.first_day_of_camp = doc.first_day_of_camp
                doc.first_day_of_camp_provided = 1

            if original.custom_discount != doc.custom_discount and doc.custom_discount:
                camp.discount = doc.custom_discount
                doc.custom_set_discount = 1
            # Shipping Address
            if original.shipping_address_1 != doc.shipping_address_1:
                camp.shipping_address_1 = doc.shipping_address_1
            if original.shipping_address_2 != doc.shipping_address_2:
                camp.shipping_address_2 = doc.shipping_address_2
            if original.shipping_address_3 != doc.shipping_address_3:
                camp.shipping_address_3 = doc.shipping_address_3

            # Billing Address
            if original.billing_address_1 != doc.billing_address_1:
                camp.billing_address_1 = doc.billing_address_1
            if original.billing_address_2 != doc.billing_address_2:
                camp.billing_address_2 = doc.billing_address_2
            if original.billing_address_3 != doc.billing_address_3:
                camp.billing_address_3 = doc.billing_address_3

            # Collected Address Flag
            if ((doc.shipping_address_1 and doc.shipping_address_2) and
                (doc.billing_address_1 and doc.billing_address_2 or doc.billing_address_same)):
                doc.collected_address = 1

            # POC Info
            if original.poc_name != doc.poc_name:
                camp.contact_name = doc.poc_name
            if original.poc_email != doc.poc_email:
                camp.email = doc.poc_email
            if original.poc_phone_number != doc.poc_phone_number:
                camp.phone = doc.poc_phone_number
            if doc.poc_name and doc.poc_email and doc.poc_phone_number:
                doc.gathered_poc_information = 1

            # Organization ID
            if original.organization_id != doc.organization_id and doc.organization_id:
                camp.organization_id = doc.organization_id
                doc.assigned_organization_id = 1

            camp.save(ignore_permissions=True)

        except frappe.DoesNotExistError:
            frappe.throw(f"Linked Camp '{doc.custom_camp_link}' not found.")

    except Exception as e:
        frappe.msgprint(f"❌ Failed to update the Camp information for {doc.name}")
        frappe.log_error(f"❌ Error updating camp in Onboarding for {doc.name}: {str(e)}", "manage_onboarding error")
