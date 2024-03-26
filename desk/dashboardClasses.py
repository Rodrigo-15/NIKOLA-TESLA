from datetime import date, datetime, timedelta
from collections import defaultdict
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ProcedureTracing
from .serializers import ProcedureSerializer, ProcedureTracingSerializer
from desk.models import Procedure
from rest_framework import status

class YourView(APIView):
    def get(self, request):
        usuario_id = request.GET.get("user_id")
        time_filter = request.GET.get("time_filter")

        if time_filter is None:
            return Response(
                {"error": "No se ha proporcionado un filtro de tiempo"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Consulta en caché
        cache_key = f"dashboard_data_{usuario_id}_{time_filter}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        today = date.today()
        fecha_inicio = today

        if time_filter == "1":
            fecha_inicio -= timedelta(days=90)
        elif time_filter == "2":
            fecha_inicio -= timedelta(days=180)
        elif time_filter == "3":
            fecha_inicio -= timedelta(days=365)
        elif time_filter == "4":
            fecha_inicio = datetime.strptime(f"{today.year}/01/01", "%Y/%m/%d").date()

        date_range = [fecha_inicio + timedelta(days=x) for x in range((today - fecha_inicio).days + 1)]
        date_range = {d.strftime("%d/%m/%Y"): 0 for d in date_range}

        procedures = ProcedureTracing.objects.filter(
            user_id=usuario_id,
            procedure_created_atdate_range=(fecha_inicio, today)
        ).select_related('procedure').order_by("-created_at")

        plazos = {"en_plazo": 0, "por_vencer": 0, "vencidos": 0}
        estados = {
            "iniciados": 0,
            "en_proceso": 0,
            "archivado": 0,
            "concluido": 0
        }
        dates = defaultdict(lambda: {"concluido": 0, "archivado": 0, "en_proceso": 0, "iniciados": 0})

        for tracing in procedures:
            procedure = ProcedureSerializer(tracing.procedure).data
            created_date = procedure["created_at"].split(" ")[0]
            if created_date in date_range:
                state = procedure["state"]
                state_date = procedure["state_date"]

                if state != "Archivado" and state != "Concluido":
                    plazos[
                        "vencidos" if state_date == 1 else
                        "por_vencer" if state_date == 2 else
                        "en_plazo"
                    ] += 1

                if state != "Iniciado":
                    estados[state.lower() if state != "En proceso" else "en_proceso"] += 1

                if tracing.is_finished:
                    dates[created_date]["concluido"] += 1
                elif tracing.is_archived:
                    dates[created_date]["archivado"] += 1
                else:
                    dates[created_date]["en_proceso"] += 1

                dates[created_date]["iniciados"] += 1

        # Eliminar fechas sin actividades
        dates = {date_key: date_value for date_key, date_value in dates.items() if sum(date_value.values()) != 0}

        weekGroups = defaultdict(lambda: {"iniciados": 0, "en_proceso": 0, "archivado": 0, "concluido": 0})

        for key, value in dates.items():
            fecha = datetime.strptime(key, "%d/%m/%Y")
            week_start = fecha - timedelta(days=fecha.weekday())
            week_start_str = week_start.strftime("%d/%m/%Y")

            for k in value.keys():
                weekGroups[week_start_str][k] += value[k]

        weekGroupsf = {"Semana" + str(i + 1): weekGroups[key] for i, key in enumerate(sorted(weekGroups.keys()))}

        # Guardar en caché los datos obtenidos
        your_data = {"dates": weekGroupsf,
                     "state_procedure": estados,
                     "state_date": plazos}

        cache.set(cache_key, your_data, timeout=3600)  # 1 hora de tiempo de vida de la caché
        return Response(your_data)