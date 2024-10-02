from rest_framework.response import Response
from rest_framework import status
from desk.models import Procedure, ProcedureTracing
from desk.serializers import ProcedureListSerializer, ProcedureTracingSerializer
from django.db.models import Q
from core.pagination import CustomPagination
from django.db.models.functions import TruncDate
from django.utils.dateparse import parse_date


def api_get_procedures(request):
    try:
        query = request.GET.get("query", "")
        date_str = request.GET.get("date", None)

        # Construcción de filtros dinámicos
        filters = Q()
        
        if query:
            filters &= (
                Q(code_number__icontains=query) |
                Q(subject__icontains=query) |
                Q(file__person__full_name__icontains=query) |
                Q(file__area__nombre__icontains=query) |
                Q(file__legalperson__razon_social__icontains=query) |
                Q(file__person__numero_documento__icontains=query) |
                Q(file__legalperson__numero_documento__icontains=query)
            )
        
        if date_str:
            # Convertir el string a una fecha válida
            date = parse_date(date_str)
            if date:
                filters &= Q(created_at__date=date)

        # Aplicar filtros y ordenar los resultados
        procedures = Procedure.objects.filter(filters).order_by("-code_number")

        # Paginación
        paginator = CustomPagination()
        paginated_procedures = paginator.paginate_queryset(procedures, request)
        serializer = ProcedureListSerializer(paginated_procedures, many=True)

        return paginator.get_paginated_response(serializer.data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
