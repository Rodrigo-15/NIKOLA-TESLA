from rest_framework.response import Response
from rest_framework import status
from desk.models import ProcedureTracing, Procedure


def api_approve_tracing(request):

    try:
        procedure_id = request.data["procedure_id"]
        user_id = request.data["user_id"]
        tracing_id = (
            ProcedureTracing.objects.filter(
                procedure_id=procedure_id, is_approved=False
            )
            .last()
            .id
        )
        procedure = Procedure.objects.filter(id=procedure_id).first()
        ProcedureTracing.objects.filter(id=tracing_id).update(is_approved=True)

        if procedure.is_external:
            from_area_id = (
                ProcedureTracing.objects.filter(id=tracing_id).first().from_area_id
            )

        else:
            from_area_id = (
                ProcedureTracing.objects.filter(id=tracing_id).first().to_area_id
            )
        ref_procedure_tracking_id = (
            ProcedureTracing.objects.filter(procedure_id=procedure_id).last().id
        )

        ProcedureTracing.objects.create(
            procedure_id=procedure_id,
            from_area_id=from_area_id,
            user_id=user_id,
            ref_procedure_tracking_id=ref_procedure_tracking_id,
        )

        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
