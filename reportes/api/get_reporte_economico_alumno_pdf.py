from rest_framework.response import Response
from rest_framework import status
from django.template.loader import render_to_string
from weasyprint import HTML
import os
import time
from django.db.models import Sum
from backend import settings
from admision.models import Expediente
from core.models import CargoArea
from economicos.models import Concepto, Pago
from reportes.functions import funtion_upload_file_to_s3


def api_get_reporte_economico_alumno_pdf(request):
    try:
        numero_documento = request.data.get("numero_documento")
        economicos = reporte_economico_function(numero_documento)
        #
        html_string = render_to_string("reports/reporte-economico.html", economicos)
        html = HTML(string=html_string)
        milisecond = str(int(round(time.time() * 1000)))
        folder_name = "pdf/economico/"
        pdf_file_name = "reporte-economico-{}-{}.pdf".format(
            numero_documento, milisecond
        )
        if settings.DEBUG:
            pdf_folder = os.path.join(settings.MEDIA_ROOT, folder_name)
            if not os.path.exists(pdf_folder):
                os.makedirs(pdf_folder)
            pdf_file_path = os.path.join(
                pdf_folder,
                "reporte-economico-{}-{}.pdf".format(numero_documento, milisecond),
            )
            html.write_pdf(target=pdf_file_path)
        else:
            html.write_pdf(target=pdf_file_name)

        path_return = funtion_upload_file_to_s3(pdf_file_name, folder_name)
        return Response({"path": path_return})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def reporte_economico_function(numero_documento):
    expediente = Expediente.objects.filter(
        persona__numero_documento=numero_documento, is_active=True
    ).first()
    # COSTO TOTAL PENSION
    if not expediente:
        return Response(
            {
                "error": "No se encontró el expediente para el alumno con número de documento {}".format(
                    numero_documento
                )
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    costo = expediente.programa.costo
    cuotas = expediente.programa.cuotas
    costo_total_pension = cuotas * costo

    # COSTO TOTAL MATRICULA
    cantidad_matriculas = expediente.programa.cantidad_matriculas
    concepto = Concepto.objects.filter(
        codigo__in=["531", "782"], 
        nombre__in=["MATRICULA MAESTRIA Y DOCTORADOS", "MATRICULA - POSTGRADO"]
    ).first()
    precio_matricula = 0

    if concepto:
        precio_matricula = concepto.precio
        concepto_matricula_id = concepto.id

    costo_total_matricula = cantidad_matriculas * precio_matricula

    # COSTO TOTAL DEL PROGRAMA
    costo_total_total = costo_total_pension + costo_total_matricula

    # PAGOS DE PENSION
    pagos = Pago.get_pagos_by_expediente(expediente)
    pagos_programa = pagos.filter(
        concepto__programa__codigo=expediente.programa.codigo
    ).order_by("fecha_operacion")
    suma_pagos_programa = pagos_programa.aggregate(Sum("monto"))["monto__sum"] or 0
    cantidad_pagos_programa = round((suma_pagos_programa / (costo - 1)), 0)
    cuotas_x_ciclo = round(int(cuotas / expediente.programa.cantidad_matriculas), 0)
    # PAGOS DE MATRICULA
    pagos_matricula = pagos.filter(concepto__id__in=(48, 49)).order_by(
        "fecha_operacion"
    )
    cantidad_pagos_matricula = pagos_matricula.count()
    suma_pagos_matricula = pagos_matricula.aggregate(Sum("monto"))["monto__sum"] or 0
    # PAGOS DE OTROS CONCEPTOS
    pagos_otros = pagos.exclude(concepto__id__in=(48, 49)).exclude(
        concepto__programa__codigo=expediente.programa.codigo
    )
    suma_pagos_otros = pagos_otros.aggregate(Sum("monto"))["monto__sum"] or 0
    # PAGOS TOTAL
    pagos_totales = suma_pagos_programa + suma_pagos_matricula + suma_pagos_otros
    # FECHA DE REPORTE
    from datetime import datetime

    date_now = datetime.now()
    fecha_reporte = date_now.strftime("%d/%m/%Y")
    hora_reporte = date_now.strftime("%H:%M %p")
    anio = date_now.year
    # LISTA DE PAGOS POR PENSION
    pagos_programa_list = []
    nro_cuota = 0
    saldo = 0
    pago_anterior = 0
    monto_pagado = 0
    total_pago_pension_lista = 0
    for pago in pagos_programa:
        nro_cuota += 1
        monto_pagado = pago.monto + pago_anterior
        saldo = costo_total_pension - monto_pagado
        pagos_programa_list.append(
            {
                "anio_operacion": pago.fecha_operacion.year,
                "fecha_operacion": pago.fecha_operacion.strftime("%d/%m/%Y"),
                "numero_conciliacion": pago.numero_conciliacion,
                "numero_operacion": pago.numero_operacion,
                "nro_cuota": str(nro_cuota).zfill(2),
                "cuotas": round((pago.monto / (costo - 1)), 0),
                "concepto": pago.concepto.nombre,
                "monto_cuota": str(pago.monto).replace(",", "."),
                "monto_pagado": str(monto_pagado).replace(",", "."),
                "saldo": str(saldo).replace(",", "."),
            }
        )
        pago_anterior = monto_pagado
        total_pago_pension_lista += pago.monto
    # LISTA DE PAGOS POR MATRICULA
    pagos_matricula_list = []
    total_pago_matricula_lista = 0
    pago_anterior = 0
    nro_cuota = 0
    monto_pagado = 0
    for pago in pagos_matricula:
        nro_cuota += 1
        if pago.concepto_id == 48:
            monto_pagado = pago.monto + pago_anterior
        else:
            monto_pagado = (pago.monto - 50) + pago_anterior
        saldo = costo_total_matricula - monto_pagado
        pagos_matricula_list.append(
            {
                "anio_operacion": pago.fecha_operacion.year,
                "fecha_operacion": pago.fecha_operacion.strftime("%d/%m/%Y"),
                "numero_conciliacion": pago.numero_conciliacion,
                "numero_operacion": pago.numero_operacion,
                "nro_cuota": str(nro_cuota).zfill(2),
                "concepto": pago.concepto.nombre,
                "monto_cuota": str(pago.concepto.precio).replace(",", "."),
                "monto_pagado": str(monto_pagado).replace(",", "."),
                "saldo": str(saldo).replace(",", "."),
            }
        )
        pago_anterior = monto_pagado
        if pago.concepto_id == 48:
            total_pago_matricula_lista += pago.monto
        else:
            total_pago_matricula_lista += pago.monto - 50
    # LISTA DE PAGOS POR OTROS CONCEPTOS
    pagos_otros_list = []
    total_pago_otros_lista = 0
    monto_pagado = 0
    for pago in pagos_otros:
        pagos_otros_list.append(
            {
                "anio_operacion": pago.fecha_operacion.year,
                "fecha_operacion": pago.fecha_operacion.strftime("%d/%m/%Y"),
                "numero_conciliacion": pago.numero_conciliacion,
                "numero_operacion": pago.numero_operacion,
                "concepto": pago.concepto.nombre,
                "monto_cuota": str(pago.monto).replace(",", "."),
            }
        )
        total_pago_otros_lista += pago.monto

    # ENCARGADO OFICINA
    obj_cargoarea = CargoArea.objects.filter(
        cargo__id=5, is_active=True, area__id=5
    ).first()
    area = obj_cargoarea.area.first().nombre
    return {
        "expediente": expediente,
        "costo_total_pension": str(costo_total_pension).replace(",", "."),
        "cuotas": cuotas,
        "pension": str(costo).replace(",", "."),
        "cantidad_matriculas": cantidad_matriculas,
        "costo_total_matricula": str(costo_total_matricula).replace(",", "."),
        "precio_matricula": str(precio_matricula).replace(",", "."),
        "costo_total_total": str(costo_total_total).replace(",", "."),
        "cantidad_pagos_programa": cantidad_pagos_programa,
        "suma_pagos_programa": str(suma_pagos_programa).replace(",", "."),
        "cantidad_pagos_matricula": cantidad_pagos_matricula,
        "suma_pagos_matricula": str(suma_pagos_matricula).replace(",", "."),
        "total_otros": str(total_pago_otros_lista).replace(",", "."),
        "pagos_totales": str(pagos_totales).replace(",", "."),
        "fecha_reporte": fecha_reporte,
        "hora_reporte": hora_reporte,
        "pagos_programa": pagos_programa_list,
        "pagos_matricula": pagos_matricula_list,
        "pagos_otros": pagos_otros_list,
        "total_debe_pension": str(
            costo_total_pension - total_pago_pension_lista
        ).replace(",", "."),
        "total_debe_matricula": str(
            costo_total_matricula - total_pago_matricula_lista
        ).replace(",", "."),
        "cuotas_x_ciclo": cuotas_x_ciclo,
        "cargoarea": obj_cargoarea,
        "area": area,
        "anio": anio,
    }
