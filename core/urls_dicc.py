from backend.settings import DEBUG, LOCAL_URL, PROD_URL

if DEBUG:
    url = LOCAL_URL
else:
    url = PROD_URL


urls_dicc = {
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
            "edit": f"{url}desk/procedure_procreqs/",  # put
        },
        "procedures": {
            "get": f"{url}desk/procedures/",  # get
            "save": f"{url}desk/procedures/",  # post
            "delete": f"{url}desk/procedures/",  # delete
            "edit": f"{url}desk/procedures/",  # put
        },
    },
}
