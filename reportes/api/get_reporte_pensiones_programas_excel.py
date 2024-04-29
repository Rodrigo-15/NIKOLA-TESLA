from rest_framework.response import Response
from rest_framework import status
from xlsxwriter.workbook import Workbook
import os
import time
from django.db.models import Sum
from backend import settings
from admision.models import Expediente
from economicos.models import Pago
from reportes.functions import funtion_upload_file_to_s3


def api_get_reporte_pensiones_programas_excel(request):
    try:
        programa_id = request.GET.get("programa_id")
        promocion = request.GET.get("promocion")

        if programa_id == None:
            return Response(
                {"error": "No se encontro el programa"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # path
        milisecond = str(int(round(time.time() * 1000)))
        folder_name = "excel/economicos/"
        excel_file_name = "reporte-pensiones-programa-{}-{}-{}.xlsx".format(
            programa_id, promocion, milisecond
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
            "Programa",
            "Promocion",
            "N° Pensiones",
            "M. Pensiones",
            "N° Matriculas",
            "M. Matriculas",
            "Observacion",
        )
        worksheet.write_row(0, 0, header, format_header)

        # body
        Pagos_data = reporte_pensiones_programa_function(programa_id, promocion)
        format_body = workbook.add_format({"border": 1})
        format_body_number = workbook.add_format({"num_format": "#,##0", "border": 1})
        format_body_money = workbook.add_format({"num_format": "#,##0.00", "border": 1})

        worksheet.set_column("A:L", None, format_body)
        worksheet.set_column("I:I", None, format_body_money)
        worksheet.set_column("H:H", None, format_body_number)
        worksheet.set_column("J:J", None, format_body_number)
        worksheet.set_column("K:K", None, format_body_money)
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


def reporte_pensiones_programa_function(programa_id, promocion):
    if programa_id == None:
        return Response(
            {"error": "No se encontro el programa"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if promocion == None:
        expedientes_data = Expediente.objects.filter(
            programa_id=programa_id, promocion__contains=promocion
        ).order_by(
            "persona__apellido_paterno",
            "persona__apellido_materno",
        )
    else:
        expedientes_data = Expediente.objects.filter(
            programa_id=programa_id, promocion=promocion
        ).order_by(
            "persona__apellido_paterno",
            "persona__apellido_materno",
        )

    reportes = []
    num = 0
    for exp in expedientes_data:
        # pensiones
        monto_pension = Pago.objects.filter(
            numero_documento=exp.persona.numero_documento,
            concepto__programa_id=programa_id,
        ).aggregate(Sum("monto"))["monto__sum"]
        if monto_pension == None:
            monto_pension = 0
        num_pensiones = round((monto_pension / exp.programa.costo), 0)

        # matriculas
        monto_matriculas = Pago.objects.filter(
            numero_documento=exp.persona.numero_documento,
            concepto__codigo="531",
            monto__in=[201, 251],
        ).aggregate(Sum("monto"))["monto__sum"]
        if monto_matriculas == None:
            monto_matriculas = 0
        num_matriculas = Pago.objects.filter(
            numero_documento=exp.persona.numero_documento,
            concepto__codigo="531",
            monto__in=[201, 251],
        ).count()

        # num
        num += 1

        # observacion
        observacion = ""
        if num_pensiones == 0:
            observacion = "NO TIENE PENSIONES"
        # data
        data = (
            num,
            exp.persona.numero_documento,
            exp.persona.nombres,
            exp.persona.apellido_paterno,
            exp.persona.apellido_materno,
            exp.programa.nombre,
            exp.promocion,
            num_pensiones,
            monto_pension,
            num_matriculas,
            monto_matriculas,
            observacion,
        )
        reportes.append(data)

    return reportes
