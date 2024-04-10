from rest_framework.response import Response
from rest_framework import status
from desk.models import ProcedureTracing, Procedure
from core.models import CargoArea
from desk.serializers import ProcedureTracingSerializer, ProcedureSerializer
from core.serializers import AreaSerializer
from django.db.models import Count


def api_desk_notification(request):
    try:
        user_id = request.GET.get("user_id")
        obj_notify_area = []
        obj_notify_user = []
        obj_notify_external = []
        count_notify = {
            "notify_area": 0,
            "notify_user": 0,
            "notify_external": 0,
        }
        # for area
        cargo_area = CargoArea.objects.filter(persona__user_id=user_id).first()

        if not cargo_area:
            obj_notify_area = []

        data_area = cargo_area.area.all()

        areas = AreaSerializer(data_area, many=True).data
        if areas:
            area_id = [area["id"] for area in areas]

            tracings_for_area = ProcedureTracing.objects.filter(
                to_area_id__in=area_id, is_approved=False, assigned_user_id=None
            ).order_by("-created_at")

            for tracing in tracings_for_area:
                obj_notify_area.append(
                    {
                        "procedure_id": tracing.procedure.id,
                        "message": f"{tracing.user}, te ha asignado un trámite con número {tracing.procedure.code_number}. Revisalo por favor.",
                        "date": tracing.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
        # for user
        tracings_for_user = ProcedureTracing.objects.filter(
            to_area_id__in=area_id, assigned_user_id=user_id, is_approved=False
        ).order_by("-created_at")
        for tracing in tracings_for_user:
            obj_notify_user.append(
                {
                    "procedure_id": tracing.procedure.id,
                    "message": f"{tracing.user}, te ha asignado un trámite con número {tracing.procedure.code_number}. Revisalo por favor.",
                    "date": tracing.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
        # for external
        tracings_for_external = ProcedureTracing.objects.filter(
            is_approved=False, assigned_user_id=None, from_area_id__in=area_id
        ).order_by("-created_at")
        proceduretracing = ProcedureTracingSerializer(tracings_for_external, many=True)

        procedures = Procedure.objects.filter(
            id__in=[procedure["procedure"] for procedure in proceduretracing.data],
            is_external=True,
        ).exclude(
            id__in=ProcedureTracing.objects.values("procedure_id")
            .annotate(count=Count("procedure_id"))
            .filter(count__gt=1)
            .values("procedure_id"),
        )
        procedures = ProcedureSerializer(procedures, many=True).data
        tracings_for_external = ProcedureTracing.objects.filter(
            procedure_id__in=[p["id"] for p in procedures],
            is_approved=False,
            assigned_user_id=None,
            from_area_id__in=area_id,
        ).order_by("-created_at")

        for tracing in tracings_for_external:
            obj_notify_external.append(
                {
                    "procedure_id": tracing.procedure.id,
                    "message": f"se creo un  un trámite en linea con número {tracing.procedure.code_number}. Revisalo por favor.",
                    "date": tracing.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

        count_notify["notify_area"] = len(obj_notify_area)
        count_notify["notify_user"] = len(obj_notify_user)
        count_notify["notify_external"] = len(obj_notify_external)

        return Response(
            {
                "count_notify": count_notify,
                "notify_area": obj_notify_area,
                "notify_user": obj_notify_user,
                "notify_external": obj_notify_external,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
