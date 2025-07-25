
# Import Frappe for ERPNext document and database operations
import frappe


def enqueue_lead_conversion(doc, method):
    """
    Hook function to enqueue lead conversion when a Lead document is updated.
    If the lead's custom_phase is 'Signed' and it hasn't been converted yet, triggers conversion.
    Args:
        doc: The Lead document being processed.
        method: The method triggering the hook (e.g., on_update).
    """
    # Only convert if lead is signed and not already converted
    if doc.custom_phase == "Signed" and not doc.custom_converted_to_customer:
        convert_lead_to_camp_and_customer(doc)


def convert_lead_to_camp_and_customer(doc):
    """
    Converts a Lead document to a Camp or Other Organization document if the lead is signed and not already converted.
    This function creates the appropriate organization record and marks the lead as converted to prevent duplicate processing.
    Args:
        doc: The Lead document being processed.
    """
    # Early return if lead is not signed or already converted
    if doc.custom_phase != "Signed" or doc.custom_converted_to_customer:
        print("early return")  # Log for debugging
        return  # already handled
    
    # If the organization type is Camp, create a Camp document if it doesn't exist
    if doc.custom_organization_type == "Camp":
        if not frappe.db.exists("Camp", {"organization_name": doc.company_name}):
            frappe.logger().info(f"Creating Camp for {doc.company_name}")  # Log creation for audit
            camp = frappe.new_doc("Camp")  # Create new Camp document
            camp.organization_name = doc.company_name  # Set organization name
            camp.contact_name = doc.custom_contact_name  # Set contact name
            camp.email = doc.email_id  # Set email
            camp.phone = doc.phone  # Set phone
            camp.lead_link = doc.name  # Link to lead
            camp.save(ignore_permissions=True)  # Save Camp, bypassing permissions
            frappe.msgprint(f"Camp {camp.organization_name} created")  # Notify user in UI
    else:
        # If not Camp, create Other Organization document if it doesn't exist
        if not frappe.db.exists("Other Organization", {"organization_name": doc.company_name}):
            frappe.logger().info(f"Creating Camp for {doc.company_name}")  # Log creation for audit
            other_org = frappe.new_doc("Other Organization")  # Create new Other Organization document
            other_org.organization_name = doc.company_name  # Set organization name
            other_org.contact_name = doc.custom_contact_name  # Set contact name
            other_org.email = doc.email_id  # Set email
            other_org.phone = doc.phone  # Set phone
            other_org.lead_link = doc.name  # Link to lead
            other_org.save(ignore_permissions=True)  # Save Other Organization, bypassing permissions
            frappe.msgprint(f"Other Organization: {other_org.organization_name} created")  # Notify user in UI
    # Mark the lead as converted to prevent duplicate conversion
    frappe.db.set_value("Lead", doc.name, "custom_converted_to_customer", 1)