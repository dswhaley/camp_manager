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
            camp = frappe.new_doc("Camp")
            camp.organization_name = doc.company_name
            camp.contact_name = doc.custom_contact_name
            camp.email = doc.email_id
            camp.phone = doc.phone
            camp.lead_link = doc.name
            camp.save(ignore_permissions=True)
    else:
        if not frappe.db.exists("Other Organization", {"organization_name": doc.company_name}):
            frappe.logger().info(f"Creating Camp for {doc.company_name}")
            other_org = frappe.new_doc("Other Organization")
            other_org.organization_name = doc.company_name
            other_org.contact_name = doc.custom_contact_name
            other_org.email = doc.email_id
            other_org.phone = doc.phone
            other_org.lead_link = doc.name
            other_org.save(ignore_permissions=True)
    frappe.db.set_value("Lead", doc.name, "custom_converted_to_customer", 1)