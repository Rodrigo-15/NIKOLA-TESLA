from rest_framework.response import Response
from rest_framework import status
from desk.models import ProcedureTracing


def api_finally_procedure(request):
    try:
        procedure_id = request.data["procedure_id"]
        user_id = request.data["user_id"]
        from_area_id = (
            ProcedureTracing.objects.filter(procedure_id=procedure_id)
            .last()
            .from_area_id
        )
        action = request.data["action"]
        document_response = request.FILES.get("document_response")
        ref_procedure_tracking_id = (
            ProcedureTracing.objects.filter(procedure_id=procedure_id).last().id
        )
        ProcedureTracing.objects.create(
            procedure_id=procedure_id,
            from_area_id=from_area_id,
            user_id=user_id,
            action=action,
            ref_procedure_tracking_id=ref_procedure_tracking_id,
            is_finished=True,
            document_response=document_response,
        )

        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
