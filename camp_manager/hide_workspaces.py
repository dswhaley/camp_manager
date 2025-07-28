import frappe

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
            ws.save(ignore_permissions=True)
            print(f"Workspace '{name}' hidden.")
        except frappe.DoesNotExistError:
            print(f"Workspace '{name}' not found. Skipped.")
