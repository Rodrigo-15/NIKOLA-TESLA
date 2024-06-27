from rest_framework.response import Response
from rest_framework import status
from weasyprint import HTML
import os
import time
from backend import settings
from academicos.models import Matricula, Periodo, Programa, Cursos
from admision.models import Expediente
from reportes.functions import funtion_upload_file_to_s3


def api_get_reporte_matriculas_excel(request):
    if request.method == "GET":
        try:
            return Response({"error": "Metodo no permitido"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)