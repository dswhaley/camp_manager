import frappe
import json
from datetime import datetime

@frappe.whitelist(allow_guest=True)
def create_from_google_form():
    try:
        secret_token = frappe.local.form_dict.get("secret_token")
        expected_token = frappe.db.get_single_value("Google Form Sync Settings", "secret_token")
        if not secret_token or secret_token != expected_token:
            frappe.throw("Invalid or missing secret token")

        data = frappe.local.form_dict
        camp_name = data.get("camp_name")

        if frappe.db.exists("Camp Settings", camp_name):
            print(f"Camp Settings: {camp_name} already exists")
            return

        doc = frappe.new_doc("Camp Settings")
        date = convert_datetime(data.get("first_day_of_camp"))
        doc.camp_name = data.get("camp_name")
        doc.timezone = data.get("timezone")
        doc.num_campers = data.get("num_campers")
        doc.first_day_of_camp = date
        doc.registration = data.get("registration")
        doc.how_campers_register = data.get("how_campers_register")
        doc.how_campers_enroll = data.get("how_campers_enroll")
        doc.features = data.get("features")
        doc.pos_features = data.get("pos_features")
        doc.parent_visibility = data.get("parent_visibility")
        doc.parent_deposit = data.get("parent_deposit")
        doc.camp_deposit = data.get("camp_deposit")
        doc.camp_deposit_description = data.get("camp_deposit_description")
        doc.staff_discounts = data.get("staff_discounts")
        doc.cash_refunds = data.get("cash_refunds")
        doc.refund_threshold = data.get("refund_threshold")
        doc.donated_account_ballances = data.get("donated_account_ballances")
        doc.can_campers_use_cashcredit_cards = data.get("can_campers_use_cashcredit_cards")
        doc.daily_spending_limit = data.get("daily_spending_limit")
        doc.camper_photos = data.get("camper_photos")
        doc.care_packages = data.get("care_packages")
        doc.attendance_app = data.get("attendance_app")
        doc.verify_adults = data.get("verify_adults")
        doc.camper_checkin_upon_using_wristband = data.get("camper_checkin_upon_using_wristband")
        doc.health_info_importation = data.get("health_info_importation")
        doc.parent_portal_visibility = data.get("parent_portal_visibility")
        doc.special_requests = data.get("special_requests")

        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"✅ Inserted Camp Settings with name: {doc.name}")

        link_camp_to_camp_settings(camp_name)

        return {"status": "success", "name": doc.name}

    except Exception as e:
        print("❌ Error during Camp Settings insert:")
        print(str(e))
        print(frappe.get_traceback())
        frappe.log_error(f"Error: {str(e)}\n{frappe.get_traceback()}", "Google Form Sync Error")
        return {"status": "error", "message": str(e)}

def convert_datetime(date):
    if not date:
        frappe.throw("Missing 'first_day_of_camp'")
    try:
        parsed_date = datetime.strptime(date, "%a %b %d %H:%M:%S GMT%z %Y")
        return parsed_date.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"Date Parse Error: {str(e)}")
        frappe.throw(f"Invalid date format for first_day_of_camp: {date}")

def link_camp_to_camp_settings(camp_name):
    try:
        if frappe.db.exists("Camp", camp_name):
            camp = frappe.get_doc("Camp", camp_name)
            if not camp.get("link_camp_to_camp_settings"):
                camp.link_to_camp_settings = camp_name
                camp.save(ignore_permissions=True)
        else:
            print(f"No Camp found with name: {camp_name}")
    except Exception as e:
        print(f"Link Error: {str(e)}\n{frappe.get_traceback()}")
        frappe.log_error(f"Link Error: {str(e)}\n{frappe.get_traceback()}", "Link Camp Error")