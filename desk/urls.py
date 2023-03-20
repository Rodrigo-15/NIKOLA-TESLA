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
)

urlpatterns = [
    path("", include(router.urls)),
    path("get_procedures", get_procedures, name="get_procedures"),
    path(
        "get_tracings_procedures/<int:status>",
        get_tracings_procedures,
        name="get_tracings_procedures",
    ),
    path(
        "get_dashboard_procedures",
        get_dashboard_procedures,
        name="get_dashboard_procedures",
    ),
    path("login/", login, name="login"),
    path("save_procedure", save_procedure, name="save_procedure"),
    path('update_procedure', update_procedure),
    path(
        "get_procedure_and_tracing_by_id",
        get_procedure_and_tracing_by_id,
        name="get_procedure_by_id",
    ),
    path("years_for_procedures", years_for_procedures, name="years_for_procedures"),
    path("save_derive_procedure", save_derive_procedure, name="save_derive_procedure"),
    path(
        "get_tracings_to_approved",
        get_tracings_to_approved,
        name="get_tracings_to_approved",
    ),
    path("approve_tracing", approve_tracing, name="approve_tracing"),
]
