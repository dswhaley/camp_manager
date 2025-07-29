import frappe
from frappe.exceptions import LinkValidationError

def hide_erpnext_workspaces():
    workspace_names_to_hide = [
        "Home",
        "Accounting",
        "Buying",
        "Selling",
        "Stock",
        "Assets",
        "Manufacturing",
        "Quality",
        "Projects",
        "CRM",
        "Settings"
    ]

    for name in workspace_names_to_hide:
        try:
            ws = frappe.get_doc("Workspace", name)
            ws.hidden = 1
            ws.type = "Workspace"
            try:
                ws.save(ignore_permissions=True)
                print(f"Workspace '{name}' hidden.")
            except LinkValidationError as e:
                print(f"Workspace '{name}' skipped due to broken link: {e}")
        except frappe.DoesNotExistError:
            print(f"Workspace '{name}' not found. Skipped.")
