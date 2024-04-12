from rest_framework.response import Response
from rest_framework import status
from desk.models import Anexo, ProcedureTracing


def api_anexar_procedure(request):
    try:
        procedure_id = request.data["procedure_id"]
        anexo_id = request.data["anexo_id"]
        user_id = request.data["user_id"]

        if not anexo_id or not procedure_id:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "El anexo no existe"},
            )
        # crear el anexo
        anexo = Anexo.objects.create(
            procedure_id=procedure_id,
            procedure_anexo_id=anexo_id,
        )
        if not anexo:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "No se pudo crear el anexo"},
            )
        # finalizar el tramite anexado
        from_area_id = (
            ProcedureTracing.objects.filter(procedure_id=anexo_id).last().from_area_id
        )
        ref_procedure_tracking_id = (
            ProcedureTracing.objects.filter(procedure_id=anexo_id).last().id
        )
        ProcedureTracing.objects.create(
            procedure_id=anexo_id,
            from_area_id=from_area_id,
            user_id=user_id,
            ref_procedure_tracking_id=ref_procedure_tracking_id,
            is_finished=True,
            is_anexed=True,
        )
        # mensaje anexo el tramite principal
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
            is_anexed=True,
        )

        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
