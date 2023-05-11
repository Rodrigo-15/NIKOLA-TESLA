from django.urls import include, path

from desk.router import router
from desk.views import (
    get_procedures,
    get_procedure_and_tracing_by_id,
    login,
    get_dashboard_procedures,
    get_tracings_procedures,
    save_procedure,
    update_procedure,
    years_for_procedures,
    save_derive_procedure,
    get_tracings_to_approved,
    approve_tracing,
    get_procedure_by_id,
    get_areas,
    get_user_for_area,
    finally_trace_procedure,
    get_procedures_requirements
)

urlpatterns = [
    path("", include(router.urls)),
    path("get_procedures", get_procedures, name="get_procedures"),
    path("get_tracings_procedures/<int:status>", get_tracings_procedures),
    path("get_dashboard_procedures", get_dashboard_procedures),
    path("login/", login, name="login"),
    path("save_procedure", save_procedure, name="save_procedure"),
    path('update_procedure', update_procedure),
    path("get_procedure_and_tracing_by_id", get_procedure_and_tracing_by_id),
    path("get_procedure_by_id/<int:procedure_id>", get_procedure_by_id),
    path("years_for_procedures", years_for_procedures),
    path("save_derive_procedure", save_derive_procedure),
    path("get_tracings_to_approved", get_tracings_to_approved),
    path("approve_tracing", approve_tracing, name="approve_tracing"),
    path("get_areas", get_areas, name="get_areas"),
    path("get_user_for_area", get_user_for_area, name="get_user_for_area"),
    path("finally_trace_procedure", finally_trace_procedure, name="finally_trace_procedure"),
    path("get_procedures_requirements", get_procedures_requirements, name="get_procedures_requirements"),
]
