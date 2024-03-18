from backend.settings import DEBUG, URL_LOCAL, URL_PROD

url = URL_LOCAL if DEBUG else URL_PROD

urls_dict = {
    "get_menu": f"{url}core/get_menu",
    "desk": {
        "login": f"{url}desk/login/",  # post
        "get_areas": f"{url}desk/get_areas",  # get
        "get_user_for_area": f"{url}desk/get_user_for_area",  # post
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
            "get_tracings_to_approved_for_area": f"{url}desk/get_tracings_to_approved_for_area",  # get
            "get_tracings_to_approved_for_user": f"{url}desk/get_tracings_to_approved_for_user",  # get
            "approve_tracing": f"{url}desk/approve_tracing",  # post
            "save_derive_procedure": f"{url}desk/save_derive_procedure",  # post
            "finally_procedure": f"{url}desk/finally_procedure",  # post
            "archive_procedure": f"{url}desk/archive_procedure",  # post
            "anexar_procedure": f"{url}desk/anexar_procedure",  # post
        },
        "procedure_type": {
            "get": f"{url}desk/procedure_type/",  # get
            "create": f"{url}desk/procedure_type/",  # post
            "update": f"{url}desk/procedure_type/id/",  # put
        },
        "pocedure_procreqs": {
            "get": f"{url}desk/procedure_procreqs/",  # get
            "get_procedures_requirements": f"{url}desk/get_procedures_requirements",  # post
            "create": f"{url}desk/procedure_procreqs/",  # post
            "update": f"{url}desk/procedure_procreqs/id/",  # put
        },
        "procedures": {
            "get_procedures": f"{url}desk/get_procedures",
            "get_procedures_in_started": f"{url}desk/get_procedures_in_started",
            "get_procedures_for_user": f"{url}desk/get_procedures_for_user",
            "get_procedures_in_assigned": f"{url}desk/get_procedures_in_assigned",
            "get_procedures_finished": f"{url}desk/get_procedures_finished",
            "get_procedure_and_tracing_by_id": f"{url}desk/get_procedure_and_tracing_by_id",
            "get_tracings_to_approved_for_external": f"{url}desk/get_tracings_to_approved_for_external",
            "save_procedure": f"{url}desk/save_procedure",
            "update_procedure": f"{url}desk/update_procedure",
            "get_procedure_by_id": f"{url}desk/get_procedure_by_id/",
            "get_procedures_charges": f"{url}desk/get_procedures_charges",
            "get_procedures_derivations": f"{url}desk/get_procedures_derivations",
            "create_procedure_charge": f"{url}desk/create_procedure_charge",
        },
        "reports": {
            "get_procedures_reports": f"{url}desk/get_procedures_reports",
            "get_process_tracking_sheet_pdf": url
            + "reportes/get_process_tracking_sheet_pdf/?procedure_id=",
            "get_charge_procedure_pdf": url + "reportes/get_charge_procedure_pdf/",
            "get_tramites_pendientes_excel": url
            + "reportes/get_tramites_pendientes_excel/?user_id=",
        },
        "external": {
            "save_procedure_externo": f"{url}desk/save_procedure_externo",
            "save_procedure_externo_register": f"{url}desk/save_procedure_externo_register",
            "get_procedure_and_tracing_by_code_number": f"{url}desk/get_procedure_and_tracing_by_code_number",
        },
    },
    "person": {
        "get_person_list": f"{url}core/get_person_list",  # get
        "get": f"{url}core/persona/",  # get
        "create": f"{url}core/persona/",  # post
        "update": f"{url}core/persona/",  # put
        "change_profile_image": f"{url}core/change_profile_image",
    },
    "person_legal": {
        "get": f"{url}core/persona_juridica/",  # get
        "create": f"{url}core/persona_juridica/",  # post
        "update": f"{url}core/persona_juridica/",  # put
    },
}
