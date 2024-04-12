from rest_framework.response import Response
from rest_framework import status
from desk.models import ProcedureTracing, Procedure
from desk.serializers import ProcedureTracingSerializer, ProcedureListSerializer
from django.db.models import Q
from django.db.models.functions import TruncDate
from core.pagination import CustomPagination


def api_get_procedures_reports(request):
    try:
        query = request.GET.get("query")
        date = request.GET.get("date")

        procedure_tracings = ProcedureTracing.objects.filter()

        proceduretracing = ProcedureTracingSerializer(procedure_tracings, many=True)

        procedures = Procedure.objects.filter(
            id__in=[procedure["procedure"] for procedure in proceduretracing.data]
        )
        procedures = (
            procedures.filter(
                Q(code_number__icontains=query)
                | Q(subject__icontains=query)
                | Q(file__person__full_name__icontains=query)
                | Q(file__area__nombre__icontains=query)
                | Q(file__legalperson__razon_social__icontains=query)
                | Q(file__person__numero_documento__icontains=query)
                | Q(file__legalperson__numero_documento__icontains=query),
                **({"created_at__date": date} if date else {}),
            )
            .annotate(created_at_date=TruncDate("created_at"))
            .order_by("-code_number")
        )
        paginator = CustomPagination()
        paginated_procedures = paginator.paginate_queryset(procedures, request)
        serializer = ProcedureListSerializer(paginated_procedures, many=True)

        return paginator.get_paginated_response(serializer.data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
