

# Frappe is the core framework for ERPNext, used for database and document operations
import frappe
# JSON is used for reading configuration files that map countries to currencies and associations to discounts
import json
# OS is used for file path manipulations, ensuring compatibility across environments
import os




def organization_hooks(doc, method):
    """
    Main entry point for organization-related hooks, called on document events.
    This function coordinates updates to currency, discounts, link status, and customer info
    for Camp and Other Organization doctypes. It ensures that all related business logic is
    applied consistently whenever a document is saved or updated.
    Args:
        doc: The Frappe document being processed (Camp or Other Organization).
        method: The method triggering the hook (e.g., on_update, on_submit).
    """
    if doc.country_shipping_address or doc.country_billing_address:
        check_currancy(doc)  # Ensure currency is set based on country_shipping_address field
    set_discount(doc, method)  # Apply association discount if the association has changed
    if doc.doctype == "Camp":
        update_link_status(doc, method)  # Mark camp as linked if settings are present
    update_customer_info(doc, method)  # Sync all relevant customer info from organization/camp


def check_currancy(doc):
    """
    Checks if the currency field on the document needs to be updated based on the country_shipping_address.
    This is important for international customers, ensuring that their currency matches their shipping country.
    If the document is new or the country_shipping_address has changed since the last save, currency is updated.
    Args:
        doc: The Frappe document being processed.
    """
    try:
        # For new documents, always set currency from country
        if doc.is_new():
            update_currency(doc)
            return

        # For existing documents, compare with the original to detect changes
        if not hasattr(doc, "_original"):
            doc._original = frappe.get_doc(doc.doctype, doc.name)
            original = doc._original

        # Only update currency if the country_shipping_address has changed
        if doc.country_shipping_address != original.country_shipping_address:
            update_currency(doc)
    except Exception as e:
        # Print error for debugging, but do not interrupt workflow
        print(f"Didn't update currancy due to: {str(e)}")



def update_currency(doc):
    """
    Updates the currency field of the document based on the country_shipping_address.
    Uses a local JSON file mapping countries to currencies, allowing for easy updates and customization.
    If the country is not found in the mapping, defaults to USD to avoid errors in downstream processes.
    Args:
        doc: The Frappe document being processed.
    """
    # Build the path to the country-currency mapping file (should be in the same directory)
    file_path = os.path.join(os.path.dirname(__file__), "country_currency_map.json")
    with open(file_path, "r") as file:
        country_currency = json.load(file)  # Load country-currency mapping from JSON file
        country = doc.country_shipping_address.lower()  # Normalize country name for lookup
        currency = country_currency.get(country.lower())  # Get currency for country, case-insensitive
        if currency:
            doc.currency = currency  # Set currency if found in mapping
        else:
            doc.currency = "USD"  # Default to USD if country not found (fallback)



def update_customer_info(doc, method):
    """
    Updates all customer records linked to the organization or camp document.
    This ensures that any changes to tax status, discounts, billing address, contact info, or currency
    in the organization/camp are reflected in the associated Customer records. This keeps customer data
    in sync with the latest organization/camp info, which is critical for accurate billing and reporting.
    Args:
        doc: The Frappe document being processed (Camp or Other Organization).
        method: The method triggering the hook.
    """
    customers = []  # List to hold linked customers
    cust = None
    if doc.doctype == "Camp":
        # Get all customers linked to this camp via custom_camp_link field
        if frappe.db.exists("Customer", {"custom_camp_link": doc.name}):
            cust = frappe.get_doc("Customer", {"custom_camp_link": doc.name})
    elif doc.doctype == "Other Organization":
        # Get all customers linked to this organization via custom_other_organization_link field
        if frappe.db.exists("Customer", {"custom_other_organization_link": doc.name}):
            cust = frappe.get_doc("Customer", {"custom_other_organization_link": doc.name})
    # If no customers found, nothing to update
    if cust == None:
        return
    try:

        # Update all relevant custom fields from organization/camp doc
        cust.custom_tax_status = doc.tax_exempt  # Sync tax exemption status
        cust.custom_tax_exemption_number = doc.tax_exemption_number  # Sync exemption number
        cust.custom_discount_ = doc.association_discount  # Sync association discount
        update_customer_billing_address(doc, cust)  # Update billing address fields
        cust.custom_email = doc.email  # Sync email
        cust.custom_phone = doc.phone  # Sync phone number
        cust.save(ignore_permissions=True)  # Save changes to customer

        # If the currency has changed, update customer currency and ensure account exists
        if cust.default_currency != doc.currency:
            currency = frappe.get_doc("Currency", doc.currency)
            if not currency.enabled:
                currency.enabled = 1  # Enable currency if disabled
                currency.save(ignore_permissions = True)

            first_company = frappe.get_all("Company", fields=["name"], limit=1)
            company_name = first_company[0]["name"] if first_company else None
            # Set default currency for customer in DB
            frappe.db.set_value("Customer", cust.name, "default_currency", doc.currency)
            # Ensure a child account exists for this currency
            ensure_child_account(f"Debtors {doc.currency}", doc.currency)

            # Enqueue async update for customer account to avoid blocking
            frappe.enqueue(
                "camp_manager.utils.set_customer_account",
                queue='default',
                timeout=300,
                now=False,
                is_async=True,
                company=company_name,
                account_name=f"Debtors {doc.currency} - {company_name[0]}",
                doc=doc,
                cust=cust
            )
    except Exception as e:
        # Log and print errors for debugging and support
        print(f"Failed to update customer info due to: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Customer Info Update Error")
        frappe.msgprint(f"Failed to update customer info: {str(e)}")



def set_customer_account(company, account_name, doc, cust):
    """
    Appends a new account to the customer's accounts child table, linking the customer to the correct receivable account.
    This is important for proper financial tracking and reporting in ERPNext, especially for multi-currency setups.
    Args:
        company: The company name.
        account_name: The account name to link (should match currency).
        doc: The organization/camp document (source of currency info).
        cust: The customer document to update.
    """
    # Add account entry to customer, linking to the correct company and account
    cust.append("accounts", {
        "company": company,
        "account": f"Debtors {doc.currency} - {company_name[0]}"
    })
    cust.save(ignore_permissions=True)  # Save changes to customer document



def ensure_child_account(account_name: str, currency: str):
    """
    Ensures a child account exists under Accounts Receivable for the given currency and company.
    This is essential for proper receivables tracking in multi-currency environments. If the account does not exist,
    it is created automatically. This function is used to keep financial records consistent and prevent errors in transactions.
    Args:
        account_name: Name of the child account to ensure (e.g., 'Debtors USD').
        currency: Currency for the account (e.g., 'USD').
    Returns:
        The name of the existing or newly created account.
    """
    # Step 1: Find the Accounts Receivable parent for this company (should be unique per company)
    first_company = frappe.get_all("Company", fields=["name"], limit=1)
    company_name = first_company[0]["name"] if first_company else None

    # Get parent account for Accounts Receivable (must exist)
    parent_account = frappe.get_value("Account", {
        "name": f"Accounts Receivable - {company_name[0]}",
        "company": company_name
    })

    # If parent account not found, raise error to prevent orphaned accounts
    if not parent_account:
        raise ValueError(f"Accounts Receivable parent not found for company '{company_name}'")
    # Step 2: Check if the child account already exists to avoid duplicates
    existing_account = frappe.db.exists("Account", {
        "account_name": account_name,
        "parent_account": parent_account,
        "company": company_name
    })

    # If child account exists, return its name for reference
    if existing_account:
        print(f"✅ Account '{account_name}' already exists under '{parent_account}'")
        return existing_account

    # Step 3: Create the account if it doesn't exist, with correct type and currency
    account = frappe.get_doc({
        "doctype": "Account",
        "account_name": account_name,
        "parent_account": parent_account,
        "is_group": 0,
        "root_type": "Asset",
        "account_type": "Receivable",
        "account_currency": currency,
        "company": company_name
    })

    account.insert(ignore_permissions=True)  # Insert new account into database
    #frappe.db.commit()  # Commit if needed (usually handled by Frappe)

    print(f"✅ Created new child account '{account.name}' under '{parent_account}'")
    return account.name
       






def update_link_status(doc, method):
    """
    Updates the settings_status field if the document is linked to camp settings.
    This is used to visually indicate in the UI that a camp is properly linked to its settings,
    which can affect downstream logic and user workflows.
    Args:
        doc: The Frappe document being processed.
        method: The method triggering the hook.
    """
    if doc.link_to_camp_settings:
        doc.settings_status = "Linked"




def set_discount(doc, method):
    """
    Sets the association discount for the document based on the discounts.json file.
    This allows for flexible discount management by simply updating the JSON file, without code changes.
    Handles file not found and JSON errors gracefully to avoid breaking the save process.
    Args:
        doc: The Frappe document being processed.
        method: The method triggering the hook.
    """
    try:
        # Uncomment below if you want to skip discount for new docs
        # if doc.is_new():
        #     return

        original = None
        # Retrieve original document for comparison, to detect association changes
        if not doc.is_new() and not hasattr(doc, "_original"):
            doc._original = frappe.get_doc(doc.doctype, doc.name)
            original = doc._original

        # If association changed or original is missing, update discount from JSON
        if original == None or (original.association != doc.association) and doc.association:
            file_path = os.path.join(os.path.dirname(__file__), "discounts.json")

            with open(file_path, "r") as file:
                association_discounts = json.load(file)  # Load discounts from JSON file

                if doc.association in association_discounts:
                    doc.association_discount = association_discounts[doc.association]  # Set discount if found

    except FileNotFoundError as fne:
        # Handle missing discounts.json file gracefully, log for admin review
        print(f"Failed due to FileNotFoundError: {str(fne)}")
        frappe.log_error("Could not find discounts.json", "Discount Error")

    except json.JSONDecodeError as jsnde:
        # Handle invalid JSON format, log for admin review
        print(f"Failed due to json.JSONDecodeError: {str(jsnde)}")
        frappe.log_error("Invalid JSON format in discounts.json", "Discount Error")

    except Exception as e:
        # Log any other errors for debugging and support
        print(f"Failed due to: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Unexpected error in set_discount")






def update_customer_billing_address(doc, cust):
    """
    Updates the billing address fields on the customer document from the organization/camp document.
    Prefers billing address fields, falls back to shipping address if billing is incomplete or missing.
    This ensures that customer records always have a valid address for billing and communication, reducing errors in invoices and correspondence.
    Args:
        doc: The organization/camp document (source of address info).
        cust: The customer document to update.
    """
    # Prepare the new address by collecting all required fields
    parts = []
    # Use billing address if all required fields are present (most accurate for invoices)
    if doc.street_address_line_1_billing_address and doc.city_billing_address and doc.state_billing_address and doc.zip_code_billing_address and doc.country_billing_address:
        parts = [
            doc.street_address_line_1_billing_address,
            doc.street_address_line_2_billing_address,
            doc.city_billing_address,
            doc.state_billing_address,
            doc.zip_code_billing_address,
            doc.country_billing_address
        ]
    # Otherwise, use shipping address if all required fields are present (fallback)
    elif doc.street_address_line_1_shipping_address and doc.city_shipping_address and doc.state_shipping_address and doc.zip_code_shipping_address and doc.country_shipping_address:
        parts = [
            doc.street_address_line_1_shipping_address,
            doc.street_address_line_2_shipping_address,
            doc.city_shipping_address,
            doc.state_shipping_address,
            doc.zip_code_shipping_address,
            doc.country_shipping_address
        ]

    # Assign address fields to customer if all are present (must be exactly 6 fields)
    for i in range(0, len(parts)):
        if len(parts) == 6:
            cust.custom_street_address_line_1 = parts[0]
            cust.custom_street_address_line_2 = parts[1]
            cust.custom_city = parts[2]
            cust.custom_state = parts[3]
            cust.custom_zip_code = parts[4]
            cust.custom_country = parts[5]



def set_customer_billing_from_organization(doc, method):
    """
    Placeholder for future implementation to set customer billing from organization.
    This function can be expanded to handle more complex billing logic, such as syncing additional fields or handling edge cases.
    Args:
        doc: The organization/camp document.
        method: The method triggering the hook.
    """
    pass