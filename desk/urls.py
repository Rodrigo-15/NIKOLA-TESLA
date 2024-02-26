from django.urls import include, path

from desk.router import router
from desk.views import (
    get_procedure_and_tracing_by_id,
    get_dashboard_procedures,
    get_tracings_procedures,
    update_procedure,
    years_for_procedures,
    save_derive_procedure,
    approve_tracing,
    get_areas,
    get_user_for_area,
    finally_procedure,
    get_procedures_requirements,
    get_user_profile,
    # new views
    login,
    get_procedures,
    get_procedures_in_started,
    get_procedures_for_user,
    get_procedures_in_assigned,
    save_procedure,
    get_procedure_by_id,
    get_tracings_to_approved_for_area,
    get_tracings_to_approved_for_user,
)

urlpatterns = [
    path("", include(router.urls)),
    # new paths
    path("login/", login, name="login"),
    path("get_procedures", get_procedures, name="get_procedures"),
    path(
        "get_procedures_in_started",
        get_procedures_in_started,
        name="get_procedures_in_started",
    ),
    path(
        "get_procedures_in_assigned",
        get_procedures_in_assigned,
        name="get_procedures_in_assigned",
    ),
    path(
        "get_procedures_for_user",
        get_procedures_for_user,
        name="get_procedures_for_user",
    ),
    path("get_procedure_by_id/<int:procedure_id>", get_procedure_by_id),
    path("get_procedure_and_tracing_by_id", get_procedure_and_tracing_by_id),
    path("get_user_for_area", get_user_for_area, name="get_user_for_area"),
    path("save_procedure", save_procedure, name="save_procedure"),
    path("update_procedure", update_procedure),
    path("save_derive_procedure", save_derive_procedure),
    path(
        "finally_procedure",
        finally_procedure,
        name="finally_procedure",
    ),
    path("get_tracings_to_approved_for_area", get_tracings_to_approved_for_area),
    path("get_tracings_to_approved_for_user", get_tracings_to_approved_for_user),
    path("approve_tracing", approve_tracing, name="approve_tracing"),
    # OLD
    path("get_tracings_procedures/<int:status>", get_tracings_procedures),
    path("get_dashboard_procedures", get_dashboard_procedures),
    path("years_for_procedures", years_for_procedures),
    path("get_areas", get_areas, name="get_areas"),
    path(
        "get_procedures_requirements",
        get_procedures_requirements,
        name="get_procedures_requirements",
    ),
    path("get_user_profile", get_user_profile, name="get_user_profile"),
]
