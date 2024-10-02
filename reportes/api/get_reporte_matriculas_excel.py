from rest_framework.response import Response
from rest_framework import status
from xlsxwriter.workbook import Workbook
import os
import time
from backend import settings
from academicos.models import Matricula, Programa
from admision.models import Expediente
from reportes.functions import funtion_upload_file_to_s3


def api_get_reporte_matriculas_excel(request):
    if request.method == "GET":
        try:
            periodo_id = request.GET.get("periodo_id")
            if periodo_id == None:
                return Response(
                    {"error": "No se encontro el periodo"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # path
            milisecond = str(int(round(time.time() * 1000)))
            folder_name = "excel/academicos/"
            excel_file_name = "Reporte-matriculas-periodo-{}-{}.xlsx".format(
                periodo_id, milisecond
            )
            # EXCEL
            if settings.DEBUG:
                excel_folder = os.path.join(settings.MEDIA_ROOT, folder_name)
                if not os.path.exists(excel_folder):
                    os.makedirs(excel_folder)
                workbook = Workbook(
                    os.path.join(settings.MEDIA_ROOT, folder_name, f"{excel_file_name}")
                )
            else:
                workbook = Workbook(excel_file_name)

            worksheet = workbook.add_worksheet()
            # header
            format_header = workbook.add_format(
                {
                    "bold": 1,
                    "border": 1,
                    "align": "center",
                    "valign": "vcenter",
                    "bg_color": "#D9D9D9",
                }
            )
            header = (
                "PROGRAMA",
                "MATRICULADOS",
                "EGRESADOS",

            )
            worksheet.write_row(0, 0, header, format_header)

            # data
            
            
            workbook.close()
            # upload to s3
            if not settings.DEBUG:
                funtion_upload_file_to_s3(excel_file_name, folder_name)

            return Response(
                {"url": f"{settings.MEDIA_URL}{folder_name}{excel_file_name}"},
                status=status.HTTP_200_OK,
            )


        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)