from django.db.models import Count, OuterRef, Subquery, Q
from rest_framework.pagination import PageNumberPagination
from desk.models import Procedure, ProcedureTracing
from desk.serializers import ProcedureListSerializer, ProcedureTracingSerializer
from core.models import CargoArea
from core.serializers import AreaSerializer
from core.pagination import CustomPagination
from rest_framework.response import Response
from rest_framework import status


def api_get_procedures_in_assigned(request):
    try:
        user_id = request.GET.get("user_id")
        query = request.GET.get("query")
        cargo_area = CargoArea.objects.filter(persona__user_id=user_id).first()
        if not cargo_area:
            areas = []
        else:
            data_area = cargo_area.area.all()
            areas = AreaSerializer(data_area, many=True).data

        latest_procedure_tracing_ids = (
            ProcedureTracing.objects.filter(
                user_id=user_id,
                from_area_id__in=[area["id"] for area in areas],
            )
            .order_by("procedure_id", "-created_at")
            .distinct("procedure_id")
            .values_list("id", flat=True)
        )
        latest_dates_subquery = (
            ProcedureTracing.objects.filter(procedure_id=OuterRef("pk"))
            .order_by("-created_at")
            .values("created_at")[:1]
        )

        procedure_tracings = (
            ProcedureTracing.objects.filter(
                id__in=latest_procedure_tracing_ids,
                is_finished=False,
                is_approved=False,
                to_area_id__isnull=True,
            )
            .exclude(
                procedure_id__in=ProcedureTracing.objects.filter(
                    is_finished=True
                ).values("procedure_id")
            )
            .exclude(
                procedure_id__in=ProcedureTracing.objects.values("procedure_id")
                .annotate(count=Count("procedure_id"))
                .filter(count=1)
                .values("procedure_id"),
            )
            .exclude(
                id__lt=Subquery(
                    ProcedureTracing.objects.filter(
                        user_id=user_id, procedure_id=OuterRef("procedure_id")
                    )
                    .order_by("-id")
                    .values("id")[:1]
                )
            )
            .order_by("-created_at")
        )

        procedures = (
            Procedure.objects.filter(id__in=procedure_tracings.values("procedure_id"))
            .annotate(latest_tracing_date=Subquery(latest_dates_subquery))
            .order_by("latest_tracing_date")
        )

        procedures = procedures.filter(
            Q(code_number__icontains=query)
            | Q(subject__icontains=query)
            | Q(file__person__full_name__icontains=query)
            | Q(file__area__nombre__icontains=query)
            | Q(file__legalperson__razon_social__icontains=query)
            | Q(file__person__numero_documento__icontains=query)
            | Q(file__legalperson__numero_documento__icontains=query),
        )

        paginator = CustomPagination()
        paginated_procedures = paginator.paginate_queryset(procedures, request)
        serializer = ProcedureListSerializer(paginated_procedures, many=True)
        return paginator.get_paginated_response(serializer.data)

    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
