
# App metadata for ERPNext
app_name = "camp_manager"
app_title = "Camp Manager"
app_publisher = "Funfangle"
app_description = "This app keeps track of the information for all Camps by storing them in Camp and Camp Settings Doctypes. It also creates a Camp and Camp Settings entry whenever a ERPnext customer is created"
app_email = "danielwhaleygcc@gmail.com"
app_license = "mit"

# Import API for Google Form sync
from camp_manager.api import create_entry

# Fixtures ensure customizations (fields, workflows, scripts, etc.) are exported/imported with the app
fixtures = [
    {
        "dt": "DocType",
        "filters": [
            ["name", "in", ["Camp", "Camp Settings", "Onboarding", "Other Organization", "Google Form Sync Settings"]]
        ]
    },
    # Custom fields for Lead and Customer doctypes
    {
        "dt": "Custom Field",
        "filters": [["dt", "in", ["Lead", "Onboarding", "Customer"]]]
    },
    {
        "dt": "Property Setter",
        "filters": [["doc_type", "=", "Lead"]]
    },
    {
        "dt": "Workflow",
        "filters": [["document_type", "=", "Lead"]]
    },
    {
        "dt": "Client Script",
        "filters": [["dt", "=", "Lead"]]
    },
    {
        "dt": "Print Format",
        "filters": [["doc_type", "=", "Lead"]]
    },
    {
        "doctype": "Property Setter",
        "filters": [["doc_type", "=", "Customer"]]
    },
    # Module definition for Camp
 {
        "doctype": "Module Def",
        "filters": [["module_name", "in", [
            "Camp Manager", 
            "Camp"
        ]]]
    },

    # Workspaces for navigation and dashboards
    {
        "doctype": "Workspace",
        "filters": [
            ["name", "in", ["Organization Info", "Home Page"]]
        ]
    }
]


# Override whitelisted methods for custom API endpoints
override_whitelisted_methods = {
    "camp_manager.api.create_entry.create_from_google_form": "camp_manager.api.create_entry.create_from_google_form"
}



# doc_events map document events (like on_update, before_save) to Python functions
# This is the heart of the app's business logic integration with ERPNext
doc_events = {
    "Lead": {
        # When a Lead is updated, check if it should be converted to a Camp/Customer
        "on_update": "camp_manager.lead_hooks.enqueue_lead_conversion"
    },
    "Camp": {
        # When a Camp is updated, create related Customer/Onboarding if needed
        "on_update": "camp_manager.organization_hooks.organization_creation",
        # Before saving a Camp, run organization hooks for currency, discount, etc.
        "before_save": "camp_manager.utils.organization_hooks"
    },
    "Other Organization": {
        # When an Other Organization is updated, create related Customer/Onboarding if needed
        "on_update": "camp_manager.organization_hooks.organization_creation",
        # Before saving, run organization hooks for currency, discount, etc.
        "before_save": "camp_manager.utils.organization_hooks"
    },
    "Onboarding": {
        # Before saving Onboarding, update phase and sync with linked org/camp
        "before_save": "camp_manager.onboarding_hooks.manage_onboarding"
    }
}