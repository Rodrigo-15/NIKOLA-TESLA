from rest_framework.response import Response
from rest_framework import status
from desk.models import Procedure, ProcedureTracing
from desk.serializers import ProcedureListSerializer, ProcedureTracingSerializer
from django.db.models import Q, Count
from core.pagination import CustomPagination


def api_get_procedures_in_started(request):
    try:
        user_id = request.GET.get("user_id")
        query = request.GET.get("query")

        procedure_tracings = ProcedureTracing.objects.filter(
            is_finished=False,
            procedure_id__in=ProcedureTracing.objects.values("procedure_id")
            .annotate(count=Count("procedure_id"))
            .filter(count=1)
            .values("procedure_id"),
        )

        proceduretracing = ProcedureTracingSerializer(procedure_tracings, many=True)

        procedures = Procedure.objects.filter(
            id__in=[procedure["procedure"] for procedure in proceduretracing.data]
        )
        procedures = procedures.filter(
            Q(code_number__icontains=query)
            | Q(subject__icontains=query)
            | Q(file__person__full_name__icontains=query)
            | Q(file__area__nombre__icontains=query)
            | Q(file__legalperson__razon_social__icontains=query)
            | Q(file__person__numero_documento__icontains=query)
            | Q(file__legalperson__numero_documento__icontains=query),
            user_id=user_id,
        ).order_by("-code_number")
        paginator = CustomPagination()
        paginated_procedures = paginator.paginate_queryset(procedures, request)
        serializer = ProcedureListSerializer(paginated_procedures, many=True)

        return paginator.get_paginated_response(serializer.data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
