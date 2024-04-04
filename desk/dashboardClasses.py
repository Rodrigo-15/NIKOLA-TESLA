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

class YourView(APIView):
    def get(self, request, wantsData: bool):
        try:
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
            if cached_data != None:
                if cached_data[1] == "data" and wantsData == True:
                    return Response(cached_data[0])
                elif cached_data[1] == "dates" and wantsData == False:
                    return Response(cached_data[0])
            
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

            procedures = [
                    {**procedure, "created_at": procedure["created_at"].split(" ")[0]}
                    for procedure in procedures
                ] 

            for l in range(len(procedures)):
                    if procedures[l]['created_at'] not in date_range:   #tomamos solo los tramites que fueron creados en nuestro rango de tiempo
                        procedures[l] = 0

            thing = [procedure for procedure in procedures if procedure != 0]

            procedures = thing
            
            if wantsData:
                plazos = {"en_plazo": 0, "por_vencer": 0, "vencidos" : 0}
                estados = {
                    "iniciados": 0,
                    "en_proceso": 0, 
                    "archivado": 0, 
                    "concluido": 0}
                
                for procedure in procedures:            
                    state = procedure["state"]
                    state_date = procedure["state_date"]

                    if state != "Archivado" and state != "Concluido":

                        plazos[
                            "vencidos" if state_date == 1 else
                            "por_vencer" if state_date == 2 else
                            "en_plazo"
                        ] += 1

                    if state != "Iniciado":

                        estados[
                            state.lower() if state != "En proceso" else "en_proceso"
                        ] += 1

            #--------obtenemos el area del usuario-----------#

                if usuario_id == None:
                    return Response(
                        {"error": "No se encontro el usuario"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                
                cargo_area = CargoArea.objects.filter(persona__user_id=usuario_id).first()
                
                if not cargo_area:
                    return Response(
                        status=status.HTTP_400_BAD_REQUEST,
                        data={"message": "El usuario no tiene un area asignada"},
                    )

                areas = (AreaSerializer(cargo_area.area, many=True).data)

                returnList = []


                for area in areas:
                    # Fetching all tracings for the current area
                    tracings_for_user = ProcedureTracing.objects.select_related('procedure').filter(user_id=usuario_id, from_area_id=area["id"]).order_by("-created_at")

                    procedure_ids = [tracing.procedure_id for tracing in tracings_for_user]
                    procedures = Procedure.objects.filter(id__in=procedure_ids)

                    serialized_procedures = ProcedureSerializer(procedures, many=True).data

                    # Filtering procedures based on date range
                    filtered_procedures = [procedure for procedure in serialized_procedures if procedure['created_at'].split(" ")[0] in date_range]

                    plazosareas = {"en_plazo": 0, "por_vencer": 0, "vencidos": 0}
                    estadosareas = {"iniciados": 0, "en_proceso": 0, "archivado": 0, "concluido": 0}

                    for procedure in filtered_procedures:
                        state = procedure["state"]
                        state_date = procedure["state_date"]

                        if state != "Archivado" and state != "Concluido":
                            plazosareas[
                                "vencidos" if state_date == 1 else
                                "por_vencer" if state_date == 2 else
                                "en_plazo"
                            ] += 1

                        if state != "Iniciado":
                            estadosareas[state.lower() if state != "En proceso" else "en_proceso"] += 1

                    returnList.append({"area": area["nombre"], "state_procedure": estadosareas, "state_date": plazosareas})

                    
                listaAreas = returnList

                dashboard_data = {
                            "state_procedure" : estados,
                            "state_date" : plazos,
                            "area_procedures": listaAreas}
                cache.set(cache_key, [dashboard_data, "data"], timeout=3600)  # 1 hora de tiempo de vida de la caché
                print(dashboard_data)
                return Response(dashboard_data)
            else:
                dates = defaultdict(lambda: {"concluido": 0, "archivado": 0, "en_proceso": 0, "iniciados": 0})
                
                trakins = ProcedureTracingSerializer(ProcedureTracing.objects.filter(procedure_id__in =[procedure["id"] for procedure in procedures]).order_by("-created_at"), many = True).data

            # Procesar trakins y procedures juntos
                for item in trakins:
                    fecha = item["created_at"].split("T")[0].replace("-", "/")
                    año, mes, dia = fecha.split("/")
                    fecha = f"{dia}/{mes}/{año}"

                    # Actualizar los conteos correspondientes en el diccionario
                    if item.get("is_finished"):
                        dates[fecha]["concluido"] += 1
                    elif item.get("is_archived"):
                        dates[fecha]["archivado"] += 1
                    else:
                        dates[fecha]["en_proceso"] += 1

                for procedure in procedures:
                    fecha = procedure["created_at"].split("T")[0].replace("-", "/")
                    dia, mes, año = fecha.split("/")
                    fecha = f"{dia}/{mes}/{año}"


                    for datel in date_range:
                        if fecha == datel:
                            dates[datel]['iniciados'] += 1
                i = 0

                for l in range(len(dates)):
                    try:
                        a = dates[i]["iniciados"] + dates[i]["en_proceso"] + dates[i]["concluido"] +dates[i]["archivado"]
                        if a == 0:
                            dates.pop(i)
                        else:
                            i += 1
                    except IndexError:
                        break

                weekGroups = {}

                for key, value in dates.items():
                    try:
                        fecha = datetime.strptime(key, "%Y/%m/%d")
                    except ValueError:
                        fecha = datetime.strptime(key, "%d/%m/%Y")

                    week_start = fecha - timedelta(days=fecha.weekday())
                    week_start_str = week_start.strftime("%d/%m/%Y")

                    if week_start_str in weekGroups:
                        weekGroup = weekGroups[week_start_str]
                        weekGroup['iniciados'] += value["iniciados"]
                        weekGroup['en_proceso'] += value["en_proceso"]
                        weekGroup['archivado'] += value["archivado"]
                        weekGroup['concluido'] += value["concluido"]
                    else:
                        weekGroups[week_start_str] = {
                            "iniciados": value["iniciados"],
                            "en_proceso": value["en_proceso"],
                            "archivado": value["archivado"],
                            "concluido": value["concluido"]
                        }

                        
                weekGroupsf = {}
                lista = [week for week in weekGroups.keys()]
                for i in range(len(weekGroups)):
                    weekGroupsf[f"Semana{i+1}"] = weekGroups[lista[i]]



                dashboard_dates = {"dates": weekGroupsf}

                cache.set(cache_key, [dashboard_dates, "dates"], timeout=3600)  # 1 hora de tiempo de vida de la caché
                print(dashboard_dates)
                return Response(dashboard_dates)
                    
                # Guardar en caché los datos obtenidos
            
        except Exception as e:
            print("Error "+e)
            return None