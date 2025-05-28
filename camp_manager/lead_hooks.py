import frappe

def handle_lead_conversion(doc, method):
    # Check if the lead is marked as converted and hasn't already triggered automation
    if doc.custom_phase == "Signed" and not doc.custom_converted_to_customer:
        # If a Customer with this name doesn't exist, create one
        if not frappe.db.exists("Customer", {"customer_name": doc.title}):
            customer = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": doc.title,
                "lead_name": doc.name,  # Use doc.name to link back to the actual Lead
                "customer_type": "Company"
            })
            customer.insert()

        # Set the flag to prevent re-processing
        doc.converted_to_customer = 1
        doc.db_update()

        # Create Camp if it doesn't exist
        if not frappe.db.exists("Camp", {"camp_name": doc.title}):
            camp = frappe.get_doc({
                "doctype": "Camp",
                "camp_name": doc.title,
                "contact_name": doc.custom_contact_name,
                "email": doc.email_id,
                "phone": doc.phone
            })
            camp.insert()
