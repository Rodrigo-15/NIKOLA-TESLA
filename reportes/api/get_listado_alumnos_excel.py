from rest_framework.response import Response
from rest_framework import status
from xlsxwriter.workbook import Workbook
import os
import time
from backend import settings
from academicos.models import Matricula
from reportes.functions import funtion_upload_file_to_s3


def api_get_listado_alumnos_excel(request):
    try:
        cursogrupo_id = request.GET.get("cursogrupo_id")
        if cursogrupo_id == None:
            return Response(
                {"error": "No se encontro el curso"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # path
        milisecond = str(int(round(time.time() * 1000)))
        folder_name = "excel/academicos/"
        excel_file_name = "Lista-alumnos-curso-{}-{}.xlsx".format(
            cursogrupo_id, milisecond
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
            "N°",
            "N° Documento",
            "Nombres",
            "Primer Apellido",
            "Segundo Apellido",
            "Correo",
            "celular",
            "Programa",
            "Promocion",
        )
        worksheet.write_row(0, 0, header, format_header)

        # body
        Pagos_data = reporte_list_curso(cursogrupo_id)
        format_body = workbook.add_format({"border": 1})

        worksheet.set_column("A:I", None, format_body)
        # DATA
        rowDefiner = 1
        for pag in Pagos_data:
            worksheet.write_row(rowDefiner, 0, pag)
            rowDefiner += 1

        workbook.close()
        path_return = funtion_upload_file_to_s3(excel_file_name, folder_name)
        return Response({"path": path_return})

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def reporte_list_curso(cursogrupo_id):
    if cursogrupo_id == None:
        return Response(
            {"error": "No se encontro el curso"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    expedientes_data = Matricula.objects.filter(
        curso_grupo_id=cursogrupo_id, is_retirado=False
    ).order_by(
        "expediente__persona__apellido_paterno",
        "expediente__persona__apellido_materno",
    )

    reportes = []
    num = 0
    for exp in expedientes_data:
        # num
        num += 1

        # data
        data = (
            num,
            exp.expediente.persona.numero_documento,
            exp.expediente.persona.nombres,
            exp.expediente.persona.apellido_paterno,
            exp.expediente.persona.apellido_materno,
            exp.expediente.persona.correo,
            exp.expediente.persona.celular,
            exp.expediente.programa.nombre,
            exp.expediente.promocion,
        )
        reportes.append(data)

    return reportes
