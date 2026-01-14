GLOBAL_PERMISSION = {
    "superadmin": {
        "can_view_project": True,
        "can_create_task": True,
        "can_edit_task": True,
        "can_delete_task": True,
        "can_add_member": True,
        "can_remove_member": True,
        "can_update_project": True,
        "can_delete_project": True,
    },
    "staff": {
        "can_view_project": True,
        "can_create_task": True,
        "can_edit_task": True,
        "can_delete_task": False,
        "can_add_member": False,
        "can_remove_member": False,
        "can_update_project": False,
        "can_delete_project": False,
    },
    "user": {
        "can_view_project": False,  # only project-based
        "can_create_task": False,
        "can_edit_task": False,
        "can_delete_task": False,
        "can_add_member": False,
        "can_remove_member": False,
        "can_update_project": False,
        "can_delete_project": False,
    },
}
