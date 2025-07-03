app_name = "camp_manager"
app_title = "Camp Manager"
app_publisher = "Funfangle"
app_description = "This app keeps track of the information for all Camps by storing them in Camp and Camp Settings Doctypes. It also creates a Camp and Camp Settings entry whenever a ERPnext customer is created"
app_email = "danielwhaleygcc@gmail.com"
app_license = "mit"


fixtures = [
    {
        "dt": "DocType",
        "filters": [
            ["name", "in", ["Camp", "Camp Settings", "Onboarding", "Other Organization"]]
        ]
    },
    {
        "dt": "Custom Field",
        "filters": [["dt", "=", "Lead"]]
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
        "doctype": "Custom Field",
        "filters": [["dt", "=", "Customer"]]
    },
    {
        "doctype": "Property Setter",
        "filters": [["doc_type", "=", "Customer"]]
    },
        {
        "doctype": "Module Def",
        "filters": [["module_name", "=", "Camp"]]
    },
        {
        "doctype": "Workspace",
        "filters": [["name", "=", "Organization Info"]]
    }
]


doc_events = {
    "Lead": {
        "on_update": "camp_manager.lead_hooks.enqueue_lead_conversion"
    },
    "Camp": {
        "before_save": "camp_manager.utils.camp_hooks"
    },
    "Customer": {
        "before_save": "camp_manager.utils.set_customer_billing_from_camp"
    },
     "Onboarding":{
         "before_save": "camp_manager.onboarding_hooks.manage_onboarding"
    }
}


# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "camp_manager",
# 		"logo": "/assets/camp_manager/logo.png",
# 		"title": "Camp Manager",
# 		"route": "/camp_manager",
# 		"has_permission": "camp_manager.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/camp_manager/css/camp_manager.css"
# app_include_js = "/assets/camp_manager/js/camp_manager.js"

# include js, css files in header of web template
# web_include_css = "/assets/camp_manager/css/camp_manager.css"
# web_include_js = "/assets/camp_manager/js/camp_manager.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "camp_manager/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "camp_manager/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "camp_manager.utils.jinja_methods",
# 	"filters": "camp_manager.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "camp_manager.install.before_install"
# after_install = "camp_manager.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "camp_manager.uninstall.before_uninstall"
# after_uninstall = "camp_manager.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "camp_manager.utils.before_app_install"
# after_app_install = "camp_manager.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "camp_manager.utils.before_app_uninstall"
# after_app_uninstall = "camp_manager.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "camp_manager.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"camp_manager.tasks.all"
# 	],
# 	"daily": [
# 		"camp_manager.tasks.daily"
# 	],
# 	"hourly": [
# 		"camp_manager.tasks.hourly"
# 	],
# 	"weekly": [
# 		"camp_manager.tasks.weekly"
# 	],
# 	"monthly": [
# 		"camp_manager.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "camp_manager.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "camp_manager.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "camp_manager.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["camp_manager.utils.before_request"]
# after_request = ["camp_manager.utils.after_request"]

# Job Events
# ----------
# before_job = ["camp_manager.utils.before_job"]
# after_job = ["camp_manager.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"camp_manager.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

