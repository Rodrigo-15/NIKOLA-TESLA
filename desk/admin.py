from django.contrib import admin

from desk.models import (
    File,
    Procedure,
    Procedure_ProcReq,
    ProcedureRequirement,
    ProcedureTracing,
    ProcedureType,
    procedureAction,
)

# Register your models here.

admin.site.register(File)
admin.site.register(ProcedureRequirement)
admin.site.register(ProcedureType)
admin.site.register(Procedure)
admin.site.register(Procedure_ProcReq)
admin.site.register(ProcedureTracing)
admin.site.register(procedureAction)
