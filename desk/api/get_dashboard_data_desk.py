from desk.models import Procedure, ProcedureTracing
from desk.serializers import ProcedureListSerializer, ProcedureTracingSerializer
from core.models import CargoArea
from core.serializers import AreaSerializer
from django.db.models import Count, Subquery, OuterRef
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response


def api_get_dashboard_data_desk(request):
    user_id = request.GET.get("user_id")
    return_obj = {}
    try:
        area_procedures = []
        cargo_area = CargoArea.objects.filter(persona__user_id=user_id).first()
        if not cargo_area:
            areas = []
        data_area = cargo_area.area.all()
        areas = AreaSerializer(data_area, many=True).data
        primer_dia_del_mes = timezone.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        # # USUARIO
        # # POR PLAZOS
        user_procedures = {
            "state_date": {"en_plazo": 0, "por_vencer": 0, "vencidos": 0},
            "state_procedure": {"iniciados": 0, "en_proceso": 0, "concluido": 0},
        }
        state_date = {"en_plazo": 0, "por_vencer": 0, "vencidos": 0}
        state_procedure = {"iniciados": 0, "en_proceso": 0, "concluido": 0}
        procedure_tracings = (
            ProcedureTracing.objects.filter(
                is_finished=False,
                is_approved=False,
                from_area_id__in=[area["id"] for area in areas],
                to_area_id__isnull=True,
                user_id=user_id,
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
        )

        proceduretracing = ProcedureTracingSerializer(procedure_tracings, many=True)

        procedures = Procedure.objects.filter(
            id__in=[procedure["procedure"] for procedure in proceduretracing.data]
        )
        serializer = ProcedureListSerializer(procedures, many=True)
        en_plazo = 0
        por_vencer = 0
        vencidos = 0
        for procedure in serializer.data:
            if procedure["state_date"] == 1:
                en_plazo += 1
            elif procedure["state_date"] == 2:
                por_vencer += 1
            elif procedure["state_date"] == 3:
                vencidos += 1

        state_date["en_plazo"] = en_plazo
        state_date["por_vencer"] = por_vencer
        state_date["vencidos"] = vencidos

        # POR ESTADOS
        state_procedure = {"iniciados": 0, "en_proceso": 0, "concluido": 0}

        procedure_starter = ProcedureTracing.objects.filter(
            is_finished=False,
            user_id=user_id,
            procedure_id__in=ProcedureTracing.objects.values("procedure_id")
            .annotate(count=Count("procedure_id"))
            .filter(count=1)
            .values("procedure_id"),
            created_at__gte=primer_dia_del_mes,
        )
        state_procedure["iniciados"] = procedure_starter.count()
        procedure_in_progress = (
            ProcedureTracing.objects.filter(
                is_finished=False,
                is_approved=False,
                from_area_id__in=[area["id"] for area in areas],
                to_area_id__isnull=True,
                user_id=user_id,
                created_at__gte=primer_dia_del_mes,
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
        )
        state_procedure["en_proceso"] = procedure_in_progress.count()
        procedure_finished = ProcedureTracing.objects.filter(
            is_archived=False,
            is_finished=True,
            user_id=user_id,
            created_at__gte=primer_dia_del_mes,
        ).exclude(
            procedure_id__in=ProcedureTracing.objects.filter(
                is_finished=True, is_archived=True
            ).values("procedure_id")
        )
        state_procedure["concluido"] = procedure_finished.count()
        # append to user_procedures
        user_procedures["state_date"] = state_date
        user_procedures["state_procedure"] = state_procedure
        # areas
        for area in areas:
            area_nombre = area["nombre"]
            # POR ESTADOS
            procedure_starter = ProcedureTracing.objects.filter(
                is_finished=False,
                from_area_id=area["id"],
                procedure_id__in=ProcedureTracing.objects.values("procedure_id")
                .annotate(count=Count("procedure_id"))
                .filter(count=1)
                .values("procedure_id"),
                created_at__gte=primer_dia_del_mes,
            )
            procedure_in_progress = (
                ProcedureTracing.objects.filter(
                    is_finished=False,
                    is_approved=False,
                    from_area_id=area["id"],
                    to_area_id__isnull=True,
                    created_at__gte=primer_dia_del_mes,
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
            )
            procedure_finished = ProcedureTracing.objects.filter(
                is_archived=False,
                is_finished=True,
                from_area_id=area["id"],
                created_at__gte=primer_dia_del_mes,
            ).exclude(
                procedure_id__in=ProcedureTracing.objects.filter(
                    is_finished=True, is_archived=True
                ).values("procedure_id")
            )
            # por plazos
            procedure_tracings = (
                ProcedureTracing.objects.filter(
                    is_finished=False,
                    is_approved=False,
                    from_area_id=area["id"],
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
            )

            proceduretracing = ProcedureTracingSerializer(procedure_tracings, many=True)

            procedures = Procedure.objects.filter(
                id__in=[procedure["procedure"] for procedure in proceduretracing.data]
            )
            serializer = ProcedureListSerializer(procedures, many=True)
            en_plazo = 0
            por_vencer = 0
            vencidos = 0
            for procedure in serializer.data:
                if procedure["state_date"] == 1:
                    en_plazo += 1
                elif procedure["state_date"] == 2:
                    por_vencer += 1
                elif procedure["state_date"] == 3:
                    vencidos += 1

            area_procedures.append(
                {
                    "area": area_nombre,
                    "state_procedure": {
                        "iniciados": procedure_starter.count(),
                        "en_proceso": procedure_in_progress.count(),
                        "concluido": procedure_finished.count(),
                    },
                    "state_date": {
                        "en_plazo": en_plazo,
                        "por_vencer": por_vencer,
                        "vencidos": vencidos,
                    },
                }
            )

        return_obj["user_procedures"] = user_procedures
        return_obj["area_procedures"] = area_procedures
        return Response(return_obj, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
