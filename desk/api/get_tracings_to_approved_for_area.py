from rest_framework.response import Response
from rest_framework import status
from desk.models import ProcedureTracing, Procedure
from core.models import CargoArea
from core.serializers import AreaSerializer
from django.db.models import Q
from desk.serializers import ProcedureTracingSerializer, ProcedureListSerializer
from core.pagination import CustomPagination


def api_get_tracings_to_approved_for_area(request):
    try:
        user_id = request.GET.get("user_id")
        query = request.GET.get("query")
        cargo_area = CargoArea.objects.filter(persona__user_id=user_id).first()

        if not cargo_area:
            areas = []

        data_area = cargo_area.area.all()

        areas = AreaSerializer(data_area, many=True).data
        if not areas:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "El usuario no tiene un area asignada"},
            )
        area_id = [area["id"] for area in areas]
        tracings_for_area = ProcedureTracing.objects.filter(
            to_area_id__in=area_id, is_approved=False, assigned_user_id=None
        ).order_by("-created_at")
        proceduretracing = ProcedureTracingSerializer(tracings_for_area, many=True)

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
        ).order_by("-code_number")
        paginator = CustomPagination()
        paginated_procedures = paginator.paginate_queryset(procedures, request)
        serializer = ProcedureListSerializer(paginated_procedures, many=True)

        return paginator.get_paginated_response(serializer.data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
