from backend.settings import DEBUG, URL_LOCAL, URL_PROD

url = URL_LOCAL if DEBUG else URL_PROD

urls_dict = {
    "desk": {
       "headquarters": {
            "get": f"{url}desk/headquarters/",  # get
            "save": f"{url}desk/headquarters/",  # post
            "delete": f"{url}desk/headquarters/",  # delete
            "edit": f"{url}desk/headquarters/",  # put
        },
        "procedure_requirement": {
            "get": f"{url}desk/procedure_requirement/",  # get
            "save": f"{url}desk/procedure_requirement/",  # post
            "delete": f"{url}desk/procedure_requirement/",  # delete
            "edit": f"{url}desk/procedure_requirement/",  # put
        },
        "procedure_type": {
            "get": f"{url}desk/procedure_type/",  # get
            "save": f"{url}desk/procedure_type/",  # post
            "delete": f"{url}desk/procedure_type/",  # delete
            "edit": f"{url}desk/procedure_type/",  # put
        },
        "pocedure_procreqs": {
            "get": f"{url}desk/procedure_procreqs/",  # get
            "save": f"{url}desk/procedure_procreqs/",  # post
            "delete": f"{url}desk/procedure_procreqs/",  # delete
            "edit": f"{url}desk/procedure_procreqs/id/",  # put
        },
        "procedures": {
            "get": f"{url}desk/procedures/",  # get
            "get_procedure": f"{url}desk/get_procedure",  # get
            "save": f"{url}desk/procedures/",  # post
            "delete": f"{url}desk/procedures/",  # delete
            "edit": f"{url}desk/procedures/",  # put
        },
        "login": f"{url}desk/login/",
        "create_procedure": f"{url}desk/procedures/", # post
        "update_procedure": f"{url}desk/procedures/id/", # put
    },
    "core": {
        "menu": {
            "get_menu": f"{url}core/get_menu",  # get
        },
    }
}
