from rest_framework.response import Response
from rest_framework import status
from desk.models import ProcedureTracing, Procedure
from core.models import CargoArea
from django.db.models import Q, Count
from desk.serializers import ProcedureTracingSerializer, ProcedureListSerializer
from core.serializers import AreaSerializer
from core.pagination import CustomPagination


def api_get_procedures_derivations(request):
    try:
        user_id = request.GET.get("user_id")
        query = request.GET.get("query")
        date = request.GET.get("date")
        cargo_area = CargoArea.objects.filter(persona__user_id=user_id).first()
        if not cargo_area:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "El usuario no tiene un area asignada"},
            )
        data_area = cargo_area.area.all()
        areas = AreaSerializer(data_area, many=True).data

        trackins = (
            ProcedureTracing.objects.filter(
                user_id=user_id,
                from_area_id__in=[area["id"] for area in areas],
                to_area_id__isnull=False,
                procedure_charge__isnull=True,
                is_finished=False,
                is_archived=False,
            )
            .exclude(
                procedure_id__in=ProcedureTracing.objects.filter(
                    is_finished=True,
                ).values("procedure_id")
            )
            .exclude(
                procedure_id__in=ProcedureTracing.objects.values("procedure_id")
                .annotate(count=Count("procedure_id"))
                .filter(count=1)
                .values("procedure_id")
            )
            .order_by("-created_at")
        )
        proceduretracing = ProcedureTracingSerializer(trackins, many=True)

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
            **({"created_at__date": date} if date else {}),
        ).order_by("-code_number")
        paginator = CustomPagination()
        paginated_procedures = paginator.paginate_queryset(procedures, request)
        serializer = ProcedureListSerializer(paginated_procedures, many=True)
        return paginator.get_paginated_response(serializer.data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
