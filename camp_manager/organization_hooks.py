import frappe

def organization_creation(doc, method):
    if not doc.customer_and_onboarding_created:
        try:
            customer = None
            if doc.doctype == "Camp":
                if not frappe.db.exists("Customer", {"customer_name": doc.organization_name}):
                    frappe.logger().info(f"Creating Customer for {doc.organization_name}")
                    customer = frappe.new_doc("Customer")
                    customer.customer_name = doc.organization_name
                    customer.lead_name = doc.lead_link
                    customer.custom_camp_link = doc.organization_name
                    customer.customer_type = "Company"
                    customer.save(ignore_permissions=True)

            elif doc.doctype == "Other Organization":
                if not frappe.db.exists("Customer", {"customer_name": doc.organization_name}):
                    frappe.logger().info(f"Creating Customer for {doc.organization_name}")
                    customer = frappe.new_doc("Customer")
                    customer.customer_name = doc.organization_name
                    customer.lead_name = doc.lead_link
                    customer.custom_other_organization_link = doc.organization_name
                    customer.customer_type = "Company"
                    customer.save(ignore_permissions=True)
            print("Checking if onboarding exists")
            if not frappe.db.exists("Onboarding", {"title": doc.organization_name}):
                onboarding = frappe.new_doc("Onboarding")
                onboarding.name = doc.organization_name  
                onboarding.title = doc.organization_name 
                onboarding.organization_type = doc.doctype
                if doc.doctype != "Camp":
                    onboarding.registration_identified = 1
                    onboarding.first_day_of_camp_provided = 1
                onboarding.save(ignore_permissions=True)
                frappe.db.set_value(doc.doctype, doc.organization_name, "customer_and_onboarding_created", 1)
                
        except Exception as e:
            frappe.msgprint(f"Failed to create Customer and Onboarding due to: {str(e)}")