from rest_framework.decorators import api_view
from desk.NAMES import APP_NAME
from core.decorators import check_app_name, check_credentials, check_is_auth
from desk.api import (
    api_generete_code_hash,
    api_get_dashboard_data_desk,
    api_get_dashboard_dates_desk,
    api_get_procedures_in_assigned,
    api_get_procedure_and_tracing_by_id,
    api_desk_notification,
    api_save_procedure_action,
    api_get_tracings_to_approved_for_user,
    api_save_procedure_externo_register,
    api_get_tracings_to_approved_for_external,
    api_save_procedure_externo,
    api_get_procedure_and_tracing_by_code_number,
    api_get_procedures_reports,
    api_create_procedure_charge,
    api_get_procedures_derivations,
    api_get_procedures_charges,
    api_anexar_procedure,
    api_archive_procedure,
    api_get_procedures_finished,
    api_get_procedures_requirements,
    api_finally_procedure,
    api_approve_tracing,
    api_get_tracings_to_approved_for_area,
    api_save_derive_procedure,
    api_update_procedure,
    api_save_procedure,
    api_get_user_for_area,
    api_get_areas,
    api_get_procedure_by_id,
    api_get_procedures_for_user,
    api_get_procedures_in_started,
    api_get_procedures,
    api_login,
    api_get_action_procedure,
)


@api_view(["POST"])
@check_app_name(APP_NAME)
@check_credentials()
def login(request):
    if request.method == "POST":
        return api_login(request)


@api_view(["GET"])
def generete_code_hash(request):
    if request.method == "GET":
        return api_generete_code_hash(request)


@api_view(["GET"])
def get_procedures(request):
    if request.method == "GET":
        return api_get_procedures(request)


@api_view(["GET"])
def get_procedures_in_started(request):
    if request.method == "GET":
        return api_get_procedures_in_started(request)


@api_view(["GET"])
def get_procedures_in_assigned(request):
    if request.method == "GET":
        return api_get_procedures_in_assigned(request)


@api_view(["GET"])
def get_procedures_for_user(request):
    if request.method == "GET":
        return api_get_procedures_for_user(request)


@api_view(["GET"])
def get_procedure_by_id(request, procedure_id):
    if request.method == "GET":
        return api_get_procedure_by_id(request, procedure_id)


@api_view(["GET"])
def get_procedure_and_tracing_by_id(request):
    if request.method == "GET":
        return api_get_procedure_and_tracing_by_id(request)


@api_view(["GET"])
def get_areas(request):
    if request.method == "GET":
        return api_get_areas(request)


@api_view(["POST"])
def get_user_for_area(request):
    if request.method == "POST":
        return api_get_user_for_area(request)


@api_view(["POST"])
def save_procedure(request):
    if request.method == "POST":
        return api_save_procedure(request)


@api_view(["POST"])
def update_procedure(request):
    if request.method == "POST":
        return api_update_procedure(request)


@api_view(["POST"])
def save_derive_procedure(request):
    if request.method == "POST":
        return api_save_derive_procedure(request)


@api_view(["GET"])
def get_tracings_to_approved_for_area(request):
    if request.method == "GET":
        return api_get_tracings_to_approved_for_area(request)


@api_view(["GET"])
def get_tracings_to_approved_for_user(request):
    if request.method == "GET":
        return api_get_tracings_to_approved_for_user(request)


@api_view(["POST"])
def approve_tracing(request):
    if request.method == "POST":
        return api_approve_tracing(request)


@api_view(["POST"])
def finally_procedure(request):
    if request.method == "POST":
        return api_finally_procedure(request)


@api_view(["POST"])
def get_procedures_requirements(request):
    if request.method == "POST":
        return api_get_procedures_requirements(request)


@api_view(["GET"])
def get_procedures_finished(request):
    if request.method == "GET":
        return api_get_procedures_finished(request)


@api_view(["POST"])
def archive_procedure(request):
    if request.method == "POST":
        return api_archive_procedure(request)


@api_view(["POST"])
def anexar_procedure(request):
    if request.method == "POST":
        return api_anexar_procedure(request)


@api_view(["GET"])
def get_procedures_charges(request):
    if request.method == "GET":
        return api_get_procedures_charges(request)


@api_view(["GET"])
def get_procedures_derivations(request):
    if request.method == "GET":
        return api_get_procedures_derivations(request)


@api_view(["POST"])
def create_procedure_charge(request):
    if request.method == "POST":
        return api_create_procedure_charge(request)


@api_view(["GET"])
def get_procedures_reports(request):
    if request.method == "GET":
        return api_get_procedures_reports(request)


@api_view(["GET"])
def get_procedure_and_tracing_by_code_number(request):
    if request.method == "GET":
        return api_get_procedure_and_tracing_by_code_number(request)


@api_view(["POST"])
def save_procedure_externo(request):
    if request.method == "POST":
        return api_save_procedure_externo(request)


@api_view(["GET"])
def get_tracings_to_approved_for_external(request):
    if request.method == "GET":
        return api_get_tracings_to_approved_for_external(request)


@api_view(["POST"])
def save_procedure_externo_register(request):
    if request.method == "POST":
        return api_save_procedure_externo_register(request)


@api_view(["GET"])
def get_dashboard_dates_desk(request):
    if request.method == "GET":
        return api_get_dashboard_dates_desk(request)


@api_view(["GET"])
def get_dashboard_data_desk(request):
    if request.method == "GET":
        return api_get_dashboard_data_desk(request)


@api_view(["GET"])
def desk_notification(request):
    if request.method == "GET":
        return api_desk_notification(request)


@api_view(["POST"])
def save_procedure_action(request):
    if request.method == "POST":
        return api_save_procedure_action(request)


@api_view(["GET"])
def get_action_procedure(request):
    if request.method == "GET":
        return api_get_action_procedure(request)
