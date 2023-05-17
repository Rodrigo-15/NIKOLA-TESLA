from backend.settings import DEBUG, URL_LOCAL, URL_PROD

url = URL_LOCAL if DEBUG else URL_PROD

urls_dict = {
    "desk": {
        "headquarters": {
            "get": f"{url}desk/headquarters/",  # get
            "create": f"{url}desk/headquarters/",  # post
            "update": f"{url}desk/headquarters/id/",  # put
        },
        "procedure_requirement": {
            "get": f"{url}desk/procedure_requirement/",  # get
            "create": f"{url}desk/procedure_requirement/",  # post
            "update": f"{url}desk/procedure_requirement/id/",  # put
        },
        "procedure_tracing": {
            # post
            "get_tracings_to_approved": f"{url}desk/get_tracings_to_approved",
            "approve_tracing": f"{url}desk/approve_tracing",  # post
            # post
            "save_derive_procedure": f"{url}desk/save_derive_procedure",
        },
        "procedure_type": {
            "get": f"{url}desk/procedure_type/",  # get
            "create": f"{url}desk/procedure_type/",  # post
            "update": f"{url}desk/procedure_type/id/",  # put
        },
        "pocedure_procreqs": {
            "get": f"{url}desk/procedure_procreqs/",  # get
            "create": f"{url}desk/procedure_procreqs/",  # post
            "update": f"{url}desk/procedure_procreqs/id/",  # put
        },
        "procedures": {
            "get_procedures": f"{url}desk/get_procedures?date&code_number",
            "get_procedure_and_tracing_by_id": f"{url}desk/get_procedure_and_tracing_by_id",
            "save_procedure": f"{url}desk/save_procedure",
            "update_procedure": f"{url}desk/update_procedure",
            "get_procedure_by_id": f"{url}desk/get_procedure_by_id/procedure_id",
            "get_process_tracking_sheet_pdf": url+"reportes/get_process_tracking_sheet_pdf/?procedure_id={procedure_id}",
        },
        "login": f"{url}desk/login/",
        "get_tracings_procedures": f"{url}desk/get_tracings_procedures/status",
        "get_dashboard_procedures": f"{url}desk/get_dashboard_procedures",
        "years_for_procedures": f"{url}desk/years_for_procedures",  # get
        "get_areas": f"{url}desk/get_areas",  # get
        "get_user_for_area": f"{url}desk/get_user_for_area",  # post
        "save_derive_procedure": f"{url}desk/save_derive_procedure",  # post
        "get_procedures_requirements": f"{url}desk/get_procedures_requirements", # post
        # post
        "finally_trace_procedure": f"{url}desk/finally_trace_procedure",
        "get_user_profile": f"{url}desk/get_user_profile",  # get
    },
    "get_menu": f"{url}core/get_menu",
    "person": {
        "get_person_list": f"{url}core/get_person_list",  # get
        "get": f"{url}core/persona/id/",  # get
        "create": f"{url}core/persona/",  # post
        "update": f"{url}core/persona/id/",  # put
    },
}
