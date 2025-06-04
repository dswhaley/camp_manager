import frappe

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
        doc.save(ignore_permissions=True)
