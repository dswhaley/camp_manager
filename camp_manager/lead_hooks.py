import frappe

def enqueue_lead_conversion(doc, method):
    if doc.custom_phase == "Signed" and not doc.custom_converted_to_customer:
        convert_lead_to_camp_and_customer(doc)

def convert_lead_to_camp_and_customer(doc):
    if doc.custom_phase != "Signed" or doc.custom_converted_to_customer:
        print("early return")
        return  # already handled
    
    if doc.custom_organization_type == "Camp":
        if not frappe.db.exists("Camp", {"organization_name": doc.company_name}):
            frappe.logger().info(f"Creating Camp for {doc.company_name}")
            camp = frappe.get_doc({
                "doctype": "Camp",
                "organization_name": doc.company_name,
                "contact_name": doc.custom_contact_name,
                "email": doc.email_id,
                "phone": doc.phone
            })
            camp.insert(ignore_permissions=True)

        if not frappe.db.exists("Customer", {"customer_name": doc.company_name}):
            frappe.logger().info(f"Creating Customer for {doc.company_name}")
            customer = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": doc.company_name,
                "lead_name": doc.name,
                "custom_camp_link": doc.company_name,
                "customer_type": "Company"
            })
            customer.insert(ignore_permissions=True)
    else:
        if not frappe.db.exists("Other_Organization", {"organization_name": doc.company_name}):
            frappe.logger().info(f"Creating Camp for {doc.company_name}")
            camp = frappe.get_doc({
                "doctype": "Other Organization",
                "organization_name": doc.company_name,
                "contact_name": doc.custom_contact_name,
                "email": doc.email_id,
                "phone": doc.phone
            })
            camp.insert(ignore_permissions=True)

        if not frappe.db.exists("Customer", {"customer_name": doc.company_name}):
            frappe.logger().info(f"Creating Customer for {doc.company_name}")
            customer = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": doc.company_name,
                "lead_name": doc.name,
                "custom_other_organization_link": doc.company_name,
                "customer_type": "Company"
            })
            customer.insert(ignore_permissions=True)

    if not frappe.db.exists("Onboarding", {"title": doc.company_name}):
        onboarding = frappe.get_doc({
            "doctype": "Onboarding",
            "name": doc.company_name,
            "title": doc.company_name,
            "organization_type": doc.custom_organization_type
        })
        if doc.custom_organization_type != "Camp":
            onboarding.registration_identified = 1
            onboarding.first_day_of_camp_provided = 1
        onboarding.insert(ignore_permissions=True)
    frappe.db.set_value("Lead", doc.name, "custom_converted_to_customer", 1)
