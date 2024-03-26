from datetime import timedelta, date, datetime
from rest_framework.response import Response
from rest_framework import status
from core.serializers import AreaSerializer
from desk.serializers import ProcedureSerializer
from core.models import CargoArea
from desk.models import (
    ProcedureTracing,
)
from desk.serializers import (
    ProcedureSerializer
)

def get_dashboard_desk_area(user_id, time_filter):

    if time_filter == None:
        return Response(
            {"error": "no a dado un filtro de tiempo"},
            status= status.HTTP_400_BAD_REQUEST,
        )
    
    #-----elegimos nuestro rango de fechas----------#
    
    today = date.today()

    fecha_inicio = ""
    
    if time_filter == "1":
        fecha_inicio = today - timedelta(days= 90)
    elif time_filter == "2":
        fecha_inicio = today - timedelta(days= 180)
    elif time_filter == "3":
        fecha_inicio = today - timedelta(days= 365)
    elif time_filter == "4":
        dia, mes, año = today.strftime("%d/%m/%Y").split("/")
        fecha_inicio = f"01/01/{año}"
        fecha_inicio = datetime.strptime(fecha_inicio, "%d/%m/%Y")
        fecha_inicio = fecha_inicio.date()

    date_range = [fecha_inicio + timedelta(days=x) for x in range((today - fecha_inicio).days + 1)]
    date_range = [d.strftime("%d/%m/%Y") for d in date_range]

    #--------obtenemos el area del usuario-----------#

    if user_id == None:
        return Response(
            {"error": "No se encontro el usuario"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    cargo_area = CargoArea.objects.filter(persona__user_id=user_id).first()
    
    if not cargo_area:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"message": "El usuario no tiene un area asignada"},
        )

    areas = (AreaSerializer(cargo_area.area, many=True).data)

    returnList = []

    for area in areas:
        #----------obtenemos todos los tramites del area--------#

        tracings_for_user = ProcedureTracing.objects.filter(
            from_area__id=area["id"]).order_by("-created_at")

        nombreArea = area["nombre"]

        procedures = []

        for tracing in tracings_for_user:
            procedure = ProcedureSerializer(tracing.procedure).data

            if procedure not in procedures:

                procedures.append(procedure)
        i = 0

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
                
        returnList.append({"area": nombreArea,
                        "state_procedure" : estados,
                        "state_date" : plazos,})

    return returnList