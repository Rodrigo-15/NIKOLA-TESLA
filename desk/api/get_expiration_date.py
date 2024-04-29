from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from datetime import datetime
from desk.models import ProcedureType
from core.views import hollydays


def api_get_expiration_date(request):
    try:
        procedure_type_id = request.data["procedure_type_id"]
        date = request.data["date"]
        # tranformar a tipo datetime
        date = datetime.strptime(date, "%Y-%m-%d")

        # Obtener el tipo de procedimiento y los días hábiles necesarios
        procedure_type = ProcedureType.objects.filter(id=procedure_type_id).first()
        procedure_type_days = procedure_type.days
        # Asumiendo que obj.created_at es un objeto datetime
        create_date = date
        # Feriados en Perú desde una api externa
        feriados = hollydays()
        # Contador para los días hábiles
        days_added = 0
        current_date = create_date

        # Bucle para contar solo días hábiles (excluyendo sábados y domingos)
        while days_added < procedure_type_days:
            current_date += timedelta(days=1)
            # Lunes=0, Domingo=6 y feriados
            if (
                current_date.weekday() < 5
                and current_date.strftime("%Y-%m-%d") not in feriados
            ):
                days_added += 1

        current_date.strftime("%Y-%m-%d")

        return Response(
            {"expiration_date": current_date.strftime("%Y-%m-%d")},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
