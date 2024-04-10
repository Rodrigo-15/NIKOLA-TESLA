from rest_framework.response import Response
from rest_framework import status
from desk.models import Procedure, ProcedureTracing, Anexo
from desk.serializers import (
    AnexoListSerializer,
    ProcedureSerializer,
    ProcedureTracingsList,
)


def api_get_procedure_and_tracing_by_id(request):
    try:
        procedure_id = request.GET.get("procedure_id")
        procedure = Procedure.objects.filter(id=procedure_id).first()
        anexos = Anexo.objects.filter(procedure_id=procedure_id)
        procedure_tracings = (
            ProcedureTracing.objects.filter(
                procedure_id=procedure_id,
            )
            .exclude(
                id__in=ProcedureTracing.objects.filter(
                    is_approved=False,
                    to_area_id__isnull=True,
                    ref_procedure_tracking_id__isnull=False,
                    procedure_id=procedure_id,
                    is_finished=False,
                ).values("id")
            )
            .order_by("-created_at")
        )

        procedure_tracings_log = ProcedureTracing.objects.filter(
            procedure_id=procedure_id
        ).order_by("-created_at")

        serializer_procedure = ProcedureSerializer(procedure)
        serializer_anexo = AnexoListSerializer(anexos, many=True)
        serializer_procedure_tracings = ProcedureTracingsList(
            procedure_tracings, many=True
        )
        serializer_procedure_tracings_log = ProcedureTracingsList(
            procedure_tracings_log, many=True
        )

        return Response(
            {
                "procedure": serializer_procedure.data,
                "anexos": serializer_anexo.data,
                "procedure_tracings": serializer_procedure_tracings.data,
                "procedure_tracings_log": serializer_procedure_tracings_log.data,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
