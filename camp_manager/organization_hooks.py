
# Import Frappe framework for ERPNext operations and database access
import frappe


def organization_creation(doc, method):
    """
    Creates Customer and Onboarding records for a Camp or Other Organization document if they do not already exist.
    This function is triggered on document update events and ensures that every organization has a corresponding Customer
    and Onboarding record in ERPNext, which is essential for downstream processes like billing, onboarding workflows, and reporting.
    Args:
        doc: The Frappe document being processed (Camp or Other Organization).
        method: The method triggering the hook (e.g., on_update).
    """
    # Only proceed if customer_and_onboarding_created flag is not set
    if not doc.customer_and_onboarding_created:
        try:
            customer = None  # Will hold the new Customer document if created
            # If the document is a Camp, create a Customer if one does not exist
            if doc.doctype == "Camp":
                # Check if a Customer with this organization_name already exists
                if not frappe.db.exists("Customer", {"customer_name": doc.organization_name}):
                    frappe.logger().info(f"Creating Customer for {doc.organization_name}")  # Log creation for audit
                    customer = frappe.new_doc("Customer")  # Create new Customer document
                    customer.customer_name = doc.organization_name  # Set customer name from organization
                    customer.lead_name = doc.lead_link  # Link to lead if available
                    customer.custom_camp_link = doc.organization_name  # Custom field for camp linkage
                    customer.customer_type = "Company"  # Set type to Company
                    customer.save(ignore_permissions=True)  # Save Customer, bypassing permissions
                    frappe.msgprint(f"Customer {customer.name} created")  # Notify user in UI
            # If the document is an Other Organization, create a Customer if one does not exist
            elif doc.doctype == "Other Organization":
                if not frappe.db.exists("Customer", {"customer_name": doc.organization_name}):
                    frappe.logger().info(f"Creating Customer for {doc.organization_name}")  # Log creation for audit
                    customer = frappe.new_doc("Customer")  # Create new Customer document
                    customer.customer_name = doc.organization_name  # Set customer name from organization
                    customer.lead_name = doc.lead_link  # Link to lead if available
                    customer.custom_other_organization_link = doc.organization_name  # Custom field for org linkage
                    customer.customer_type = "Company"  # Set type to Company
                    customer.save(ignore_permissions=True)  # Save Customer, bypassing permissions
                    frappe.msgprint(f"Customer {customer.name} created")  # Notify user in UI
            # Create Onboarding document if one does not exist for this organization
            if not frappe.db.exists("Onboarding", {"title": doc.organization_name}):
                onboarding = frappe.new_doc("Onboarding")  # Create new Onboarding document
                onboarding.name = doc.organization_name  # Set onboarding name
                onboarding.title = doc.organization_name  # Set onboarding title
                onboarding.organization_type = doc.doctype  # Set type (Camp or Other Organization)
                # For non-Camp organizations, mark onboarding steps as completed
                if doc.doctype != "Camp":
                    onboarding.registration_identified = 1  # Mark registration as identified
                    onboarding.first_day_of_camp_provided = 1  # Mark first day as provided
                onboarding.save(ignore_permissions=True)  # Save Onboarding, bypassing permissions
                # Set flag on original document to prevent duplicate creation
                frappe.db.set_value(doc.doctype, doc.organization_name, "customer_and_onboarding_created", 1)
                frappe.msgprint(f"Onboarding document for {onboarding.name} created")  # Notify user in UI
        except Exception as e:
            # If any error occurs, notify user for troubleshooting
            frappe.msgprint(f"Failed to create Customer and Onboarding due to: {str(e)}")