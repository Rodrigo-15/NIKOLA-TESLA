from desk.models import ProcedureTracing
from core.models import CargoArea
from core.serializers import AreaSerializer
from django.db.models import Count, Subquery, OuterRef
from django.utils import timezone
from datetime import timedelta
import calendar
from rest_framework import status
from rest_framework.response import Response


def api_get_dashboard_dates_desk(request):
    user_id = request.GET.get("user_id")
    cargo_area = CargoArea.objects.filter(persona__user_id=user_id).first()
    if not cargo_area:
        areas = []
    data_area = cargo_area.area.all()
    areas = AreaSerializer(data_area, many=True).data
    return_obj = {
        "dates": {},
    }
    try:
        primer_dia_del_mes = timezone.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        ultimo_dia_del_mes = (
            primer_dia_del_mes
            + timedelta(
                days=calendar.monthrange(
                    primer_dia_del_mes.year, primer_dia_del_mes.month
                )[1]
            )
        ).replace(hour=23, minute=59, second=59)

        dia_actual = primer_dia_del_mes
        i = 0
        while dia_actual < ultimo_dia_del_mes:
            inicio_semana = dia_actual - timedelta(days=dia_actual.weekday())
            fin_semana = inicio_semana + timedelta(days=6)
            i += 1

            fin_semana = min(fin_semana, ultimo_dia_del_mes)

            dia_actual = fin_semana + timedelta(days=1)
            state_procedure = {"iniciados": 0, "en_proceso": 0, "concluido": 0}
            procedure_starter = ProcedureTracing.objects.filter(
                is_finished=False,
                user_id=user_id,
                procedure_id__in=ProcedureTracing.objects.values("procedure_id")
                .annotate(count=Count("procedure_id"))
                .filter(count=1)
                .values("procedure_id"),
                created_at__range=(inicio_semana, fin_semana),
            )
            state_procedure["iniciados"] = procedure_starter.count()
            procedure_in_progress = (
                ProcedureTracing.objects.filter(
                    is_finished=False,
                    is_approved=False,
                    from_area_id__in=[area["id"] for area in areas],
                    to_area_id__isnull=True,
                    user_id=user_id,
                    created_at__range=(inicio_semana, fin_semana),
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
                created_at__range=(inicio_semana, fin_semana),
            ).exclude(
                procedure_id__in=ProcedureTracing.objects.filter(
                    is_finished=True, is_archived=True
                ).values("procedure_id")
            )
            state_procedure["concluido"] = procedure_finished.count()

            return_obj["dates"][f"Semana_{i}"] = {
                "label_semana": f"Semana {i}",
                "label_fecha": f"{inicio_semana.strftime('%d/%m/%Y')} - {fin_semana.strftime('%d/%m/%Y')}",
                "state_procedure": state_procedure,
            }
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
    return Response(return_obj, status=status.HTTP_200_OK)
