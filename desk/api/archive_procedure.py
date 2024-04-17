from rest_framework.response import Response
from rest_framework import status
from desk.models import ProcedureTracing, Procedure


def api_archive_procedure(request):
    try:
        procedure_id = request.data["procedure_id"]
        user_id = request.data["user_id"]
        from_area_id = (
            ProcedureTracing.objects.filter(procedure_id=procedure_id)
            .last()
            .from_area_id
        )
        ref_procedure_tracking_id = (
            ProcedureTracing.objects.filter(procedure_id=procedure_id).last().id
        )
        ProcedureTracing.objects.create(
            procedure_id=procedure_id,
            from_area_id=from_area_id,
            user_id=user_id,
            ref_procedure_tracking_id=ref_procedure_tracking_id,
            is_archived=True,
            is_finished=True,
            action_id=6,
        )
        code_number = Procedure.objects.filter(id=procedure_id).first().code_number

        return Response(status=status.HTTP_200_OK, data={"code_number": code_number})

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
