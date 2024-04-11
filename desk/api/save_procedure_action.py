from rest_framework.response import Response
from rest_framework import status
from desk.models import ProcedureTracing, Procedure


def api_save_procedure_action(request):
    try:
        procedure_id = request.data["procedure_id"]
        user_id = request.data["user_id"]
        number_of_sheets = (
            request.data["number_of_sheets"]
            if "number_of_sheets" in request.data
            else 0
        )
        document_response = request.FILES.get("document_response")
        action = request.data["action"]
        ref_procedure_tracking_id = (
            ProcedureTracing.objects.filter(procedure_id=procedure_id).last().id
        )
        from_area_id = (
            ProcedureTracing.objects.filter(procedure_id=procedure_id)
            .last()
            .from_area_id
        )

        procedure_tracing = (
            ProcedureTracing.objects.filter(
                is_approved=False, procedure_id=procedure_id
            )
            .exclude(to_area_id=None)
            .first()
        )

        if procedure_tracing:
            return Response(
                status=status.HTTP_202_ACCEPTED,
                data={
                    "message": "El tramite esta pendiente de aprobación por favor revise su bandeja de entrada"
                },
            )

        procedure = Procedure.objects.filter(id=procedure_id).first()
        procedure.number_of_sheets = number_of_sheets
        procedure.save()
        ProcedureTracing.objects.create(
            procedure_id=procedure_id,
            from_area_id=from_area_id,
            user_id=user_id,
            action=action,
            ref_procedure_tracking_id=ref_procedure_tracking_id,
            document_response=document_response,
            is_internal=True,
        )

        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
