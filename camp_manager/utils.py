import frappe
import json
import os


def organization_hooks(doc, method):
    check_currancy(doc)
    set_discount(doc, method)
    if doc.doctype == "Camp":
        update_link_status(doc, method)
    update_customer_info(doc, method)

def check_currancy(doc):
    try:
        if doc.is_new():
            update_currency(doc)
            return

        
        if not hasattr(doc, "_original"):
            doc._original = frappe.get_doc(doc.doctype, doc.name)
            original = doc._original

        if doc.country_shipping_address != original.country_shipping_address:
            update_currency(doc)
    except Exception as e:
        print(f"Didn't update currancy due to: {str(e)}")

def update_currency(doc):
    file_path = os.path.join(os.path.dirname(__file__), "country_currency_map.json")
    with open(file_path, "r") as file:
        country_currency = json.load(file)
        country = doc.country_shipping_address.lower()
        currency = country_currency.get(country.lower())
        if currency:
            doc.currency = currency
        else:
            doc.currency = "USD"

def update_customer_info(doc, method):
    customers = []
    if doc.doctype == "Camp":
        customers = frappe.get_all(
            "Customer",
            filters={"custom_camp_link": doc.name},
            fields=["name"]
        )
    elif doc.doctype == "Other Organization":
        customers = frappe.get_all(
            "Customer",
            filters={"custom_other_organization_link": doc.name},
            fields=["name"]
        )
   
    if not customers:
        return
    for customer in customers:
        cust = frappe.get_doc("Customer", customer.name)


        cust.custom_tax_status = doc.tax_exempt
        cust.custom_tax_exemption_number = doc.tax_exemption_number
        cust.custom_discount_ = doc.association_discount
        update_customer_billing_address(doc, cust)
        cust.custom_email = doc.email
        cust.custom_phone = doc.phone    
        cust.save(ignore_permissions=True)


        if cust.default_currency != doc.currency:
            currency = frappe.get_doc("Currency", doc.currency)
            if not currency.enabled:
                currency.enabled = 1
                currency.save(ignore_permissions = True)

            first_company = frappe.get_all("Company", fields=["name"], limit=1)
            company_name = first_company[0]["name"] if first_company else None
            
            frappe.db.set_value("Customer", cust.name, "default_currency", doc.currency)
            ensure_child_account(f"Debtors {doc.currency}", doc.currency)

            
            frappe.enqueue("camp_manager.utils.set_customer_account", queue='default', timeout=300, now=False, is_async=True, company=company_name, account_name=f"Debtors {doc.currency} - {company_name[0]}", doc=doc, cust=cust)


def set_customer_account(company, account_name, doc, cust):
    cust.append("accounts", {
        "company": company,
        "account": f"Debtors {doc.currency} - {company_name[0]}"
    })
    cust.save(ignore_permissions=True)

def ensure_child_account(account_name: str, currency: str):
    # Step 1: Find the Accounts Receivable parent for this company
    first_company = frappe.get_all("Company", fields=["name"], limit=1)
    company_name = first_company[0]["name"] if first_company else None


    parent_account = frappe.get_value("Account", {
        "name": f"Accounts Receivable - {company_name[0]}",
        "company": company_name
    })


    if not parent_account:
        raise ValueError(f"Accounts Receivable parent not found for company '{company_name}'")
    # Step 2: Check if the child already exists
    existing_account = frappe.db.exists("Account", {
        "account_name": account_name,
        "parent_account": parent_account,
        "company": company_name
    })


    if existing_account:
        print(f"✅ Account '{account_name}' already exists under '{parent_account}'")
        return existing_account


    # Step 3: Create the account if it doesn't exist
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


    account.insert(ignore_permissions=True)
    #frappe.db.commit()


    print(f"✅ Created new child account '{account.name}' under '{parent_account}'")
    return account.name
       




def update_link_status(doc, method):
    if doc.link_to_camp_settings:
        doc.settings_status = "Linked"


def set_discount(doc, method):
    try:
        # if doc.is_new():
        #     return

        original = None
        if not hasattr(doc, "_original"):
            doc._original = frappe.get_doc(doc.doctype, doc.name)
            original = doc._original

        if original == None or (original.association != doc.association and doc.association):
            file_path = os.path.join(os.path.dirname(__file__), "discounts.json")


            with open(file_path, "r") as file:
                association_discounts = json.load(file)

                if doc.association in association_discounts:
                    doc.association_discount = association_discounts[doc.association]



    except FileNotFoundError as fne:
        print(f"Failed due to FileNotFoundError: {str(fne)}")
        frappe.log_error("Could not find discounts.json", "Discount Error")


    except json.JSONDecodeError as jsnde:
        print(f"Failed due to json.JSONDecodeError: {str(jsnde)}")
        frappe.log_error("Invalid JSON format in discounts.json", "Discount Error")


    except Exception as e:
        print(f"Failed due to: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Unexpected error in set_discount")




def update_customer_billing_address(doc, cust):
    # Prepare the new address
    parts = []
    if doc.street_address_line_1_billing_address and doc.city_billing_address and doc.state_billing_address and doc.zip_code_billing_address and doc.country_billing_address:
        parts = [doc.street_address_line_1_billing_address, doc.street_address_line_2_billing_address, doc.city_billing_address, doc.state_billing_address, doc.zip_code_billing_address, doc.country_billing_address]
    elif doc.street_address_line_1_shipping_address and doc.city_shipping_address and doc.state_shipping_address and doc.zip_code_shipping_address and doc.country_shipping_address:
        parts = [doc.street_address_line_1_shipping_address, doc.street_address_line_2_shipping_address, doc.city_shipping_address, doc.state_shipping_address, doc.zip_code_shipping_address, doc.country_shipping_address]

    
    for i in range(0, len(parts)):
        if len(parts) == 6:
            cust.custom_street_address_line_1 = parts[0]
            cust.custom_street_address_line_2 = parts[1]
            cust.custom_city = parts[2]
            cust.custom_state = parts[3]
            cust.custom_zip_code = parts[4]
            cust.custom_country = parts[5]
    







def set_customer_billing_from_organization(doc, method):
    pass