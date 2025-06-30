import frappe

def enqueue_lead_conversion(doc, method):
    if doc.custom_phase == "Signed" and not doc.custom_converted_to_customer:
        frappe.enqueue(
            "camp_manager.lead_hooks.convert_lead_to_camp_and_customer",
            queue='default',
            job_name=f"convert-lead-{doc.name}",
            docname=doc.name
        )

def convert_lead_to_camp_and_customer(docname):
    doc = frappe.get_doc("Lead", docname)

    if doc.custom_phase != "Signed" or doc.custom_converted_to_customer:
        return  # already handled

    if not frappe.db.exists("Camp", {"camp_name": doc.company_name}):
        frappe.logger().info(f"Creating Camp for {doc.company_name}")
        camp = frappe.get_doc({
            "doctype": "Camp",
            "camp_name": doc.company_name,
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

    frappe.db.set_value("Lead", doc.name, "custom_converted_to_customer", 1)
