import frappe
import json
import os

def camp_hooks(doc, method):
    update_customer_billing_address(doc, method)
    update_link_status(doc, method)
    set_discount(doc, method)
    create_customer(doc, method)
def update_link_status(doc, method):
    settingsStatus = "Unlinked"
    if doc.link_to_camp_settings:
        settingsStatus = "Linked"
    frappe.db.set_value("Camp", doc.name, "settings_status", settingsStatus)

def create_customer(doc, method):
    try:
        # Ensure original doc exists so we can compare changes
        if not hasattr(doc, "_original"):

            doc._original = frappe.get_doc(doc.doctype, doc.name)

        # Only run this when link status is changed from Unlinked -> Linked
        if not doc._original.link_to_camp_settings and doc.link_to_camp_settings:
            # Avoid duplicate Customer creation
            if not frappe.db.exists("Customer", {"custom_camp_link": doc.name}):
                customer = frappe.get_doc({
                    "doctype": "Customer",
                    "customer_name": doc.name,
                    "customer_type": "Company",
                    "custom_camp_link": doc.name
                })
                customer.insert()
                frappe.db.commit()  # Only needed if you're outside request lifecycle
    except Exception as e:
        frappe.log_error(f"❌ Failed to create a customer for Camp {doc.name}: {str(e)}", "create_customer error")

def set_discount(doc, method):
    try:
        if not hasattr(doc, "_original"):
            doc._original = frappe.get_doc(doc.doctype, doc.name)
        original = doc._original  # Corrected this

        if (original.association != doc.association and doc.association):
            file_path = os.path.join(os.path.dirname(__file__), "discounts.json")

            with open(file_path, "r") as file:
                association_discounts = json.load(file)

            if doc.association in association_discounts:
                doc.association_discount = association_discounts[doc.association]

    except FileNotFoundError:
        frappe.log_error("Could not find discounts.json", "Discount Error")

    except json.JSONDecodeError:
        frappe.log_error("Invalid JSON format in discounts.json", "Discount Error")

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Unexpected error in set_discount")


def update_customer_billing_address(doc, method):
    """When a Camp is edited, update Customer billing address only if necessary."""
    customers = frappe.get_all(
        "Customer",
        filters={"custom_camp_link": doc.name},
        fields=["name"]
    )

    if not customers:
        return

    # Prepare the new address
    parts = []
    if doc.billing_address_1:
        parts = [doc.billing_address_1, doc.billing_address_2, doc.billing_address_3]
    elif doc.shipping_address_1:
        parts = [doc.shipping_address_1, doc.shipping_address_2, doc.shipping_address_3]

    new_billing_address = ', '.join(filter(None, parts)) if any(parts) else ''

    for customer in customers:
        cust = frappe.get_doc("Customer", customer.name)

        # Only update if the current address is blank or different
        if cust.custom_billing_address != new_billing_address:
            cust.custom_billing_address = new_billing_address
            cust.save(ignore_permissions=True)


def set_customer_billing_from_camp(doc, method):
    """When a Customer is updated, set billing address from linked Camp — only if it's outdated."""
    if not doc.custom_camp_link:
        return

    try:
        camp = frappe.get_doc("Camp", doc.custom_camp_link)
    except frappe.DoesNotExistError:
        return

    parts = []
    if camp.billing_address_1:
        parts = [camp.billing_address_1, camp.billing_address_2, camp.billing_address_3]
    elif camp.shipping_address_1:
        parts = [camp.shipping_address_1, camp.shipping_address_2, camp.shipping_address_3]

    new_billing_address = ', '.join(filter(None, parts)) if any(parts) else ''

    # 🛡️ Only update if different
    if doc.custom_billing_address != new_billing_address:
        doc.custom_billing_address = new_billing_address
