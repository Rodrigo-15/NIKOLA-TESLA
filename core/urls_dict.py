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
            "get": f"{url}desk/procedures/",  # get
            "get_procedure": f"{url}desk/get_procedure",  # get
            "create": f"{url}desk/procedures/",  # post
            "update": f"{url}desk/procedures/id/",  # put
        },
        "login": f"{url}desk/login/",
        "get_started_procedures": f"{url}desk/get_started_procedures", # get
        "get_finished_procedures": f"{url}desk/get_finished_procedures", # get
    },
    "get_menu": f"{url}core/get_menu",
}
