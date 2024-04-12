from rest_framework.response import Response
from rest_framework import status
from desk.models import ProcedureTracing, Procedure, Anexo
from desk.serializers import (
    ProcedureSerializer,
    AnexoListSerializer,
    ProcedureTracingsList,
)


def api_get_procedure_and_tracing_by_code_number(request):
    try:
        code_number = request.GET.get("code_number")
        code_hash = request.GET.get("code_hash")

        procedure = Procedure.objects.filter(
            code_number=code_number, code_hash=code_hash
        ).first()
        anexos = Anexo.objects.filter(procedure_id=procedure.id)
        procedure_tracings = ProcedureTracing.objects.filter(
            procedure_id=procedure.id
        ).order_by("-created_at")

        serializer_procedure = ProcedureSerializer(procedure)
        serializer_anexo = AnexoListSerializer(anexos, many=True)
        serializer_procedure_tracings = ProcedureTracingsList(
            procedure_tracings, many=True
        )

        return Response(
            {
                "procedure": serializer_procedure.data,
                "anexos": serializer_anexo.data,
                "procedure_tracings": serializer_procedure_tracings.data,
            }
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
