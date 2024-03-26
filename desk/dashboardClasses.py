from datetime import date, datetime, timedelta
from collections import defaultdict
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ProcedureTracing
from .serializers import ProcedureSerializer, ProcedureTracingSerializer
from .getdata import *
from desk.models import File, Procedure
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10

class YourView(APIView):
   # pagination_class = CustomPagination

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
        fecha_inicio = ""

        if time_filter == "1":
            fecha_inicio = today - timedelta(days=90)
        elif time_filter == "2":
            fecha_inicio = today - timedelta(days=180)
        elif time_filter == "3":
            fecha_inicio = today - timedelta(days=365)
        elif time_filter == "4":
            dia, mes, año = today.strftime("%d/%m/%Y").split("/")
            fecha_inicio = f"01/01/{año}"
            fecha_inicio = datetime.strptime(fecha_inicio, "%d/%m/%Y").date()

        date_range = [fecha_inicio + timedelta(days=x) for x in range((today - fecha_inicio).days + 1)]
        date_range = [d.strftime("%d/%m/%Y") for d in date_range]

        tracings_for_user = ProcedureTracing.objects.select_related('procedure').filter(user_id=usuario_id).order_by("-created_at")
        procedures = [ProcedureSerializer(tracing.procedure).data for tracing in tracings_for_user]

        # Procesamiento de datos...
        i = 0

        ###-------se saca el porcentaje de tramites aprobados-----------####

        filtred_trackins = ProcedureTracing.objects.filter(
            procedure_id__in=[procedure["id"] for procedure in procedures], is_approved=False, assigned_user_id=None
            ).order_by("-created_at")
        proceduretracing = ProcedureTracingSerializer(filtred_trackins, many=True)

        procedures_not_aproved = Procedure.objects.filter(
                id__in=[procedure["procedure"] for procedure in proceduretracing.data]
            )
        
        percentage_aproved = (len(procedures) - len(procedures_not_aproved))/len(procedures)

        ###------------------------------------------------###

        for procedure in procedures:
            procedure["created_at"] = procedure["created_at"].split(" ")[0]  #tomamos solo la fecha, la hora no nos importa

        for l in range(len(procedures)):
                if procedures[l]['created_at'] not in date_range:   #tomamos solo los tramites que fueron creados en nuestro rango de tiempo
                    procedures[l] = 0

        thing = [procedure for procedure in procedures if procedure != 0]

        procedures = thing
        
        plazos = {"en_plazo": 0, "por_vencer": 0, "vencidos" : 0}
        estados = {
            "iniciados": 0,
            "en_proceso": 0, 
            "archivados": 0, 
            "concluidos": 0}
        
        dates = defaultdict(lambda: {"finalizados": 0, "archivados": 0, "en_proceso": 0, "iniciados": 0})
        
        trakins = ProcedureTracingSerializer(ProcedureTracing.objects.filter(procedure_id__in =[procedure["id"] for procedure in procedures]).order_by("-created_at"), many = True).data

    # Procesar trakins y procedures juntos
        for data in [trakins, procedures]:
            for item in data:
                print(item)
                fecha = item["created_at"].split("T")[0].replace("-", "/")
                año, mes, dia = fecha.split("/")
                fecha = f"{dia}/{mes}/{año}"

                # Actualizar los conteos correspondientes en el diccionario
                if item.get("is_finished"):
                    dates[fecha]["finalizados"] += 1
                elif item.get("is_archived"):
                    dates[fecha]["archivados"] += 1
                else:
                    dates[fecha]["en_proceso"] += 1


        for procedure in procedures:
            for datel in date_range:
                fecha = procedure["created_at"].split("T")[0].replace("-", "/")
                dia, mes, año = fecha.split("/")
                fecha = f"{dia}/{mes}/{año}"
                if fecha == datel:
                    dates[datel]['iniciados'] += 1
        i = 0

        for l in range(len(dates)):
            try:
                a = dates[i]["iniciados"] + dates[i]["en_proceso"] + dates[i]["finalizados"] +dates[i]["archivados"]
                if a == 0:
                    dates.pop(i)
                else:
                    i += 1
            except IndexError:
                break

        for procedure in procedures:
            if procedure["state"] != "Archivado" and procedure["state"] != "Concluido":
                if procedure["state_date"] == 1:
                    plazos["vencidos"] += 1
                elif procedure["state_date"] == 2:
                    plazos["por_vencer"] += 1
                elif procedure["state_date"] == 3:
                    plazos["en_plazo"] += 1

            if procedure["state"] == "Iniciado":
                estados["iniciados"] += 1
            elif procedure["state"] == "Archivado":
                estados["archivados"] += 1
            elif procedure["state"] == "Concluido":
                estados["concluidos"] += 1
            elif procedure["state"] == "En proceso":
                estados["en_proceso"] += 1

        weekGroups = {}

        for key in dates.keys():
            try:
                fecha = datetime.strptime(key, "%Y/%m/%d")
            except ValueError:
                fecha = datetime.strptime(key, "%d/%m/%Y")

            week_start = fecha - timedelta(days=fecha.weekday())

            week_start = date.strftime(week_start, "%d/%m/%Y")

            if week_start in weekGroups:
                weekGroups[week_start]['iniciados'] += dates[key]["iniciados"]
                weekGroups[week_start]['en_proceso'] += dates[key]["en_proceso"]
                weekGroups[week_start]['archivados'] += dates[key]["archivados"]
                weekGroups[week_start]['finalizados'] += dates[key]["finalizados"]
            else:
                weekGroups[week_start] = {"iniciados" : dates[key]["iniciados"],
                                        "en_proceso" : dates[key]["en_proceso"],
                                        "archivados": dates[key]["archivados"],
                                        "finalizados": dates[key]["finalizados"]}
                
        weekGroupsf = {}
        lista = [week for week in weekGroups.keys()]
        for i in range(len(weekGroups)):
            weekGroupsf[f"Semana{i+1}"] = weekGroups[lista[i]]

        listaAreas = get_dashboard_desk_area(usuario_id, time_filter)

        your_data = {"dates": weekGroupsf,
                     "state_procedure" : estados,
                     "state_date" : plazos,
                     "area_procedures": listaAreas}
            
        # Guardar en caché los datos obtenidos
        cache.set(cache_key, your_data, timeout=3600)  # 1 hora de tiempo de vida de la caché
        return Response(your_data)