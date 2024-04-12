from rest_framework.response import Response
from rest_framework import status
from desk.models import ProcedureCharge
from desk.serializers import ProcedureChargeSerializer
from core.pagination import CustomPagination
from django.db.models import Q
from django.db.models.functions import TruncDate


def api_get_procedures_charges(request):
    try:
        user_id = request.GET.get("user_id")
        query = request.GET.get("query")
        date = request.GET.get("date")

        procededure_charge = ProcedureCharge.objects.filter(
            user_id=user_id,
        )
        procededure_charge = (
            procededure_charge.filter(
                Q(correlative__icontains=query),
                **({"created_at__date": date} if date else {}),
            )
            .annotate(created_at_date=TruncDate("created_at"))
            .order_by("-correlative")
        )
        paginator = CustomPagination()
        paginated_procedures_charge = paginator.paginate_queryset(
            procededure_charge, request
        )
        serializer = ProcedureChargeSerializer(paginated_procedures_charge, many=True)

        return paginator.get_paginated_response(serializer.data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
