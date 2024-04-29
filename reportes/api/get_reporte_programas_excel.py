from rest_framework.response import Response
from rest_framework import status
from xlsxwriter.workbook import Workbook
import os
import time
from backend import settings
from economicos.models import Pago
from reportes.functions import funtion_upload_file_to_s3


def api_get_reporte_programas_excel(request):
    try:
        programa_id = request.GET.get("programa_id")
        promocion = request.GET.get("promocion")
        anio = request.GET.get("anio")
        mes = request.GET.get("mes")
        dia = request.GET.get("dia")
        # path
        milisecond = str(int(round(time.time() * 1000)))
        folder_name = "excel/economicos/"
        excel_file_name = "reporte-programa-{}-{}-{}-{}-{}.xlsx".format(
            programa_id, anio, mes, dia, milisecond
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
        header = (
            "Nombre Completo",
            "DNI",
            "N° Operacion",
            "N° conciliación",
            "Fecha de Pago",
            "Monto",
            "Concepto",
            "Programa",
            "Promocion",
        )
        worksheet.write_row(0, 0, header)

        Pagos_data = reporte_programa_function(programa_id, promocion, anio, mes, dia)

        rowDefiner = 1
        monto_total = 0
        for pag in Pagos_data:
            worksheet.write_row(rowDefiner, 0, pag)
            rowDefiner += 1
            monto_total = monto_total + float(pag[5])

        merge_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "yellow",
                "num_format": "#,##0",
            }
        )
        linea = rowDefiner + 1
        worksheet.merge_range(
            "A{}:E{}".format(linea, linea), " MONTO TOTAL", merge_format
        )
        worksheet.merge_range("F{}:I{}".format(linea, linea), monto_total, merge_format)
        workbook.close()

        path_return = funtion_upload_file_to_s3(excel_file_name, folder_name)
        return Response({"path": path_return, "cantidad": len(Pagos_data)})

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def reporte_programa_function(programa_id, promocion, anio, mes, dia):
    if programa_id == "":
        if dia == "":
            pagos_data = Pago.objects.filter(
                fecha_operacion__year__contains=anio,
                fecha_operacion__month__contains=mes,
            )
        else:
            pagos_data = Pago.objects.filter(
                expendiente__promocion__contains=promocion,
                fecha_operacion__year__contains=anio,
                fecha_operacion__month__contains=mes,
                fecha_operacion__day=dia,
            )

    else:
        if dia == "":
            pagos_data = Pago.objects.filter(
                expendiente__programa_id=programa_id,
                expendiente__promocion__contains=promocion,
                fecha_operacion__year__contains=anio,
                fecha_operacion__month__contains=mes,
            )
        else:
            pagos_data = Pago.objects.filter(
                expendiente__programa_id=programa_id,
                expendiente__promocion__contains=promocion,
                fecha_operacion__year__contains=anio,
                fecha_operacion__month__contains=mes,
                fecha_operacion__day=dia,
            )
    pagos = []
    for pago in pagos_data:
        if bool(pago.expendiente):
            programa_str = pago.expendiente.programa.nombre
            promocion_str = pago.expendiente.promocion
        else:
            programa_str = ""
            promocion_str = ""
        data = (
            pago.nombre_cliente,
            pago.numero_documento,
            pago.numero_operacion,
            pago.numero_conciliacion,
            pago.fecha_operacion.strftime("%d/%m/%Y"),
            pago.monto.__str__(),
            pago.concepto.nombre,
            programa_str,
            promocion_str,
        )
        pagos.append(data)

    return pagos
