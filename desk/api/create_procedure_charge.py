from rest_framework.response import Response
from rest_framework import status
from desk.models import ProcedureCharge, ProcedureTracing


def api_create_procedure_charge(request):
    try:
        user_id = request.data["user_id"]
        procedures = request.data["procedures"]
        procedure_charge = ProcedureCharge.objects.create(
            user_id=user_id,
        )

        for procedure in procedures:
            procedure_id = procedure["id"]
            trankins = (
                ProcedureTracing.objects.filter(
                    procedure_id=procedure_id,
                    user_id=user_id,
                    is_finished=False,
                    to_area_id__isnull=False,
                    procedure_charge__isnull=True,
                    from_area_id__isnull=False,
                )
                .order_by("-created_at")
                .first()
            )
            ProcedureTracing.objects.filter(id=trankins.id).update(
                procedure_charge_id=procedure_charge.id
            )

        return Response(
            status=status.HTTP_200_OK,
            data={
                "correlative": procedure_charge.correlative,
                "id": procedure_charge.id,
            },
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
