from desk.serializers import (
    ProcedureSerializer,
    ProcedureTracingSerializer,
    ProcedureTracingsList,
)
from datetime import timedelta, date
from datetime import datetime
from backend.settings import DEBUG, URL_LOCAL, URL_PROD
from .deskpart import *
from weasyprint import HTML
from django.template.loader import render_to_string
from csv import excel
import os
from pickle import TRUE
import time
from django.conf import settings
from django.http import HttpResponse
from academicos.models import CursoGrupo, Cursos, Aplazado
import datetime
from desk.models import Procedure, ProcedureTracing, ProcedureCharge
from xlsxwriter.workbook import Workbook
from io import BytesIO
from rest_framework.response import Response
from django.template.defaulttags import register
from django.shortcuts import render
from academicos.models import Matricula, Programa
from admision.models import Expediente
from admision.serializers.expediente import (
    ExpedienteReportSerializer,
    ExpedienteSerializer,
)
from core.models import Periodo, Persona, CargoArea, Etapa, Area
from core.serializers import AreaSerializer, PersonaSerializerFilter
from economicos.models import Concepto, Pago
from django.db.models import Sum, Max, Min
from rest_framework import status
from django.db.models import Q
from decimal import Decimal, ROUND_HALF_UP
from reportes.academicos import diploma_egresado, diploma_diplomado

#
from rest_framework.decorators import api_view
from reportes.api import (
    api_get_reporte_matricula_pdf,
    api_get_listado_alumnos_excel,
    api_get_reporte_actanotas_pdf,
    api_get_reporte_actanotas_aplazado_pdf,
    api_get_reporte_academico_alumno_pdf,
    api_get_reporte_economico_alumno_pdf,
    api_get_reporte_pensiones_programas_excel,
    api_get_reporte_programas_excel,
    api_generate_diploma_pdf,
)


@api_view(["GET"])
def get_reporte_programas_api(request):
    # Type,Date = request.GET.get('dataFetch').split(':')
    Type = "Y"
    Date = "2022"
    # expediente = reporte_matricula_alumno_function(expediente_id, periodo_id)
    data = Pago.objects.filter(id=20)
    output = BytesIO()
    workbook = Workbook(output, {"in_memory": True})
    worksheet = workbook.add_worksheet()
    formatFecha = workbook.add_format({"num_format": "dd/mm/yyyy"})
    formatMoney = workbook.add_format({"num_format": "#,##0"})
    worksheet.set_column(2, 2, cell_format=formatFecha)
    worksheet.set_column(3, 3, cell_format=formatMoney)
    # worksheet.write(fila, columna, 'Some Data')
    header = (
        "Nombre Completo",
        "DNI",
        "Fecha de Pago",
        "Monto",
        "Concepto",
        "Número de conciliación",
        "Programa",
    )
    worksheet.write_row(0, 0, header)

    if Type == "Y":
        getYear = Date
        Pagos = Pago.get_pagos_by_anio(anio=getYear).values_list(
            "nombre_cliente",
            "numero_documento",
            "fecha_operacion",
            "monto",
            "concepto__codigo",
            "numero_conciliacion",
            "concepto__programa__nombre",
        )

    if Type == "M":
        getYear, getMonth = Date.split("-")
        Pagos = Pago.get_pagos_by_anio_and_mes(anio=getYear, mes=getMonth).values_list(
            "nombre_cliente",
            "numero_documento",
            "fecha_operacion",
            "monto",
            "concepto__codigo",
            "numero_conciliacion",
            "concepto__programa__nombre",
        )

    if Type == "D":
        Pagos = Pago.get_pagos_del_dia(dia=Date).values_list(
            "nombre_cliente",
            "numero_documento",
            "fecha_operacion",
            "monto",
            "concepto__codigo",
            "numero_conciliacion",
            "concepto__programa__nombre",
        )
    rowDefiner = 1
    for pag in Pagos:
        worksheet.write_row(rowDefiner, 0, pag)
        rowDefiner += 1
    workbook.close()
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        'attachment;filename="reporte-programa-{}.xlsx"'.format(Date)
    )
    return response


@api_view(["GET"])
def get_reporte_ingresos_api(request):
    Type, Date = request.GET.get("dataFetch").split(":")
    # expediente = reporte_matricula_alumno_function(expediente_id, periodo_id)
    data = Pago.objects.filter(id=20)
    print(data)
    output = BytesIO()
    workbook = Workbook(output, {"in_memory": True})
    worksheet = workbook.add_worksheet()
    formatFecha = workbook.add_format({"num_format": "dd/mm/yyyy"})
    formatMoney = workbook.add_format({"num_format": "#,##0"})
    worksheet.set_column(2, 2, cell_format=formatFecha)
    worksheet.set_column(3, 3, cell_format=formatMoney)
    # worksheet.write(fila, columna, 'Some Data')
    header = (
        "Nombre Completo",
        "DNI",
        "Fecha de Pago",
        "Monto",
        "Concepto",
        "Número de conciliación",
    )
    worksheet.write_row(0, 0, header)

    if Type == "Y":
        getYear = Date
        Pagos = Pago.get_pagos_by_anio(anio=getYear).values_list(
            "nombre_cliente",
            "numero_documento",
            "fecha_operacion",
            "monto",
            "concepto__codigo",
            "numero_conciliacion",
        )

    if Type == "M":
        getYear, getMonth = Date.split("-")
        Pagos = Pago.get_pagos_by_anio_and_mes(anio=getYear, mes=getMonth).values_list(
            "nombre_cliente",
            "numero_documento",
            "fecha_operacion",
            "monto",
            "concepto__codigo",
            "numero_conciliacion",
        )

    if Type == "D":
        Pagos = Pago.get_pagos_del_dia(dia=Date).values_list(
            "nombre_cliente",
            "numero_documento",
            "fecha_operacion",
            "monto",
            "concepto__codigo",
            "numero_conciliacion",
        )
    rowDefiner = 1
    for pag in Pagos:
        worksheet.write_row(rowDefiner, 0, pag)
        rowDefiner += 1
    workbook.close()
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        'attachment;filename="reporte-ingreso-{}.xlsx"'.format(Date)
    )
    return response


@api_view(["GET"])
def reporte_economico_alumno_api(request):
    if request.method == "GET":
        numero_documento = request.GET.get("numero_documento")

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
            codigo="531", nombre="MATRICULA MAESTRIA Y DOCTORADOS"
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
        cantidad_pagos_programa = pagos_programa.count()
        suma_pagos_programa = pagos_programa.aggregate(Sum("monto"))["monto__sum"] or 0
        # PAGOS DE MATRICULA
        pagos_matricula = pagos.filter(concepto__id__in=(48, 49)).order_by(
            "fecha_operacion"
        )
        cantidad_pagos_matricula = pagos_matricula.count()
        suma_pagos_matricula = (
            pagos_matricula.aggregate(Sum("monto"))["monto__sum"] or 0
        )
        # PAGOS DE OTROS CONCEPTOS
        pagos_otros = (
            pagos.exclude(concepto__id__in=(48, 49))
            .exclude(concepto__programa__codigo=expediente.programa.codigo)
            .order_by("fecha_operacion")
        )
        suma_pagos_otros = pagos_otros.aggregate(Sum("monto"))["monto__sum"] or 0
        # PAGOS TOTAL
        pagos_totales = suma_pagos_programa + suma_pagos_matricula + suma_pagos_otros
        # FECHA DE REPORTE
        from datetime import datetime

        date_now = datetime.now()
        fecha_reporte = date_now.strftime("%d/%m/%Y")
        hora_reporte = date_now.strftime("%H:%M %p")
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

        return Response(
            {
                "expediente": ExpedienteReportSerializer(expediente).data,
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
            }
        )


@api_view(["GET"])
def reporte_economico_expediente_api(request):
    if request.method == "GET":
        expediente_id = request.GET.get("expediente")

        expediente = Expediente.objects.filter(id=expediente_id).first()
        # COSTO TOTAL PENSION
        if not expediente:
            return Response(
                {
                    "error": "No se encontró el expediente para el alumno con número de Expediente {}".format(
                        expediente_id
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
            nombre="MATRICULA MAESTRIA Y DOCTORADOS", codigo="531"
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
        cantidad_pagos_programa = pagos_programa.count()
        suma_pagos_programa = pagos_programa.aggregate(Sum("monto"))["monto__sum"] or 0
        # PAGOS DE MATRICULA
        pagos_matricula = pagos.filter(concepto__id__in=(48, 49)).order_by(
            "fecha_operacion"
        )
        cantidad_pagos_matricula = pagos_matricula.count()
        suma_pagos_matricula = (
            pagos_matricula.aggregate(Sum("monto"))["monto__sum"] or 0
        )
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

        return Response(
            {
                "expediente": ExpedienteReportSerializer(expediente).data,
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
            }
        )


# new code NEWDESKPART
@api_view(["GET"])
def generate_txt_bach(request):
    periodo_id = request.GET.get("periodo_id")
    if periodo_id == None:
        return Response(
            {"error": "No se encontro el periodo"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    # path
    milisecond = str(int(round(time.time() * 1000)))
    media_root = settings.MEDIA_ROOT
    txt_folder = os.path.join(media_root, "txt")
    if not os.path.exists(txt_folder):
        os.makedirs(txt_folder)
    txt_file_name = os.path.join(
        txt_folder,
        "RECA-EPG-{}-{}.txt".format(periodo_id, milisecond),
    )
    if os.path.exists(txt_file_name):
        os.remove(txt_file_name)

    # TXT
    file = open(txt_file_name, "w")
    file.write("T07591300003449440843000000000000000000002023091400000000\n")
    # body
    datos = Expediente.objects.filter(periodo_id=periodo_id, is_retired=False).order_by(
        "id"
    )
    reg_detalle = "D"
    cod_servicio = "002"
    count = 0
    ref_recibo = str("").ljust(20)
    moneda = "01"
    moneda_ref = str("").ljust(14)
    resto_data = str("").ljust(50)
    imp_moratorio = str("").ljust(14)
    otros_concepto = f"{0:0162d}"
    for data in datos:
        count = count + 1
        num_documento = str(data.persona.numero_documento).ljust(20)
        nombre_alumno = str(
            f"{data.persona.apellido_paterno} {data.persona.apellido_materno} { data.persona.nombres}"
        ).ljust(40)
        num_recibo = str(f"{count:06d}").ljust(20)
        fecha_emision = datetime.datetime.now().strftime("%Y%m%d")
        fecha_vencimiento = str("").ljust(8)
        if data.programa.id == 35:
            concepto = str(f"{531:04d}").ljust(4)
        else:
            codigo_concepto = Concepto.objects.filter(
                programa_id=data.programa.id
            ).values("codigo", "precio")
            num_concepto = int(codigo_concepto[0]["codigo"])
            monto_precio = int(codigo_concepto[0]["precio"] - 1)
            concepto = f"{num_concepto:04d}"
            precio = f"{monto_precio:012d}00"
        file.write(
            f"{reg_detalle}0{cod_servicio}000{num_documento}{nombre_alumno}{num_recibo}{ref_recibo}{fecha_emision}{fecha_vencimiento}{moneda}{moneda_ref}{resto_data}{imp_moratorio}{concepto}{precio}{otros_concepto}\n"
        )
    file.close()

    # return
    path_return = os.path.join(
        settings.MEDIA_URL,
        "txt",
        "RECA-EPG-{}-{}.txt".format(periodo_id, milisecond),
    )
    path_return = path_return.replace("\\", "/")
    return Response({"path": path_return})


@api_view(["GET"])
def get_charge_procedure_pdf(request):
    user_id = request.GET.get("user_id")
    procedure_charge_id = request.GET.get("procedure_charge_id")

    if user_id == None:
        return Response(
            {"error": "No se encontro  el usuario"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    cargo_area = CargoArea.objects.filter(persona__user_id=user_id).first()
    if not cargo_area:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"message": "El usuario no tiene un area asignada"},
        )

    procedure_charge = ProcedureCharge.objects.filter(id=procedure_charge_id).first()

    text_charge_number = procedure_charge.correlative
    
    fecha = procedure_charge.created_at.strftime("%d/%m/%Y")
    hora = procedure_charge.created_at.strftime("%H:%M %p")
    anio = procedure_charge.created_at.strftime("%Y")

    idUsuarioOriginal = procedure_charge.user
    usuarioOriginal = PersonaSerializerFilter(
        Persona.objects.filter(user_id=idUsuarioOriginal).first()
    ).data

    data_area = cargo_area.area.all()
    areas = AreaSerializer(data_area, many=True).data
    usuario = Persona.objects.filter(user_id=user_id).first()

    trackins = ProcedureTracing.objects.filter(
        user_id=user_id,
        to_area_id__isnull=False,
        procedure_charge_id=procedure_charge_id,
        is_finished=False,
    )

    if trackins.count() == 0:
        return Response(
            {"error": "No se encontro el procedimiento"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    obj_procedure = []
    for trackin in trackins:
        procedure = Procedure.objects.filter(id=trackin.procedure_id).first()
        serialized_procedure = ProcedureSerializer(procedure).data
        to_area = Area.objects.filter(id=trackin.to_area_id).first()
        serialized_procedure["to_area"] = AreaSerializer(to_area).data
        serialized_procedure["action_description"] = trackin.action_description
        obj_procedure.append(serialized_procedure)

    
    final_data = {
        "area": dict(areas[0]),
        "fecha": fecha,
        "hora": hora,
        "anio": anio,
        "usuario": PersonaSerializerFilter(usuario).data,
        "procedure": obj_procedure,
        "procedure_count": len(obj_procedure),
        "charge_number": text_charge_number,
        "original_user": usuarioOriginal,
    }
    print(final_data)
    path = get_charge_procedure(final_data)
    return Response({"path": path}, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_process_tracking_sheet_pdf(request):
    procedure_id = request.GET.get("procedure_id")
    if procedure_id == None:
        return Response(
            {"error": "No se encontro el procedimiento"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    procedure = Procedure.objects.filter(id=procedure_id).first()
    if procedure == None:
        return Response(
            {"error": "No se encontro el procedimiento"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    trackins = ProcedureTracing.objects.filter(procedure_id=procedure_id)
    final_data = {
        "procedure": ProcedureSerializer(procedure).data,
        "trackins": ProcedureTracingsList(trackins, many=True).data,
    }

    path = get_process_tracking_sheet(final_data)
    return Response({"path": path}, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_constancia_registro(request):
    procedure_id = request.GET.get("procedure_id")

    if procedure_id == None:
        return Response(
            {"error": "No se encontro  el procedure"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    procedure = ProcedureSerializer(
        Procedure.objects.filter(id=procedure_id).first()
    ).data

    area = procedure["area_id"]

    if area:
        area = AreaSerializer(Area.objects.filter(id=area)).data
        print(area)
        # area = area["nombre"]
    else:
        area = "undefined"

    path = generate_constancia_de_registro([procedure, area])
    return Response({"path": path}, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_tramites_area_excel(request):
    usuario_id = request.GET.get("user_id")
    area_id = request.GET.get("area_id")
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    year = request.GET.get("year")
    state = request.GET.get("state")
    state_date = request.GET.get("state_date")

    if area_id == None:
        return Response(
            {"error": "No se encontro el area"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if usuario_id == None:
        return Response(
            {"errror": "No se encontro el usuario"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cargo_area = CargoArea.objects.filter(persona__user_id=usuario_id).first()

    persona = PersonaSerializerFilter(cargo_area.persona).data

    nombreUsuario = f'{persona["nombres"]} {persona["apellido_paterno"]} {persona["apellido_materno"]}'

    area = Area.objects.filter(id=area_id).first()
    tracings_for_user = ProcedureTracing.objects.filter(from_area=area.id).order_by(
        "-created_at"
    )

    creacion = date.today()

    procedures = []

    for tracing in tracings_for_user:
        procedure = ProcedureSerializer(tracing.procedure).data

        if procedure not in procedures:

            procedures.append(procedure)

    i = 0

    for l in range(len(procedures)):
        try:
            if state == None and state_date != None:
                a = str(procedures[i]["state_date"])
                if a != state_date:
                    procedures.pop(i)
                else:
                    i += 1
            elif state != None and state_date == None:
                if procedures[i]["state"] != state:
                    procedures.pop(i)
                else:
                    i += 1
            elif state != None and state_date != None:
                a = str(procedures[i]["state_date"])
                if procedures[i]["state"] != state or a != state_date:
                    procedures.pop(i)
                else:
                    i += 1
        except IndexError:
            break

    if fecha_fin == None and fecha_inicio == None and year == None:
        pass
    elif fecha_fin == None and fecha_inicio == None and year != None:
        fecha_inicio = f"{year}-01-01"
        fecha_fin = f"{year}-12-31"
        fecha_inicio = date(*map(int, fecha_inicio.split("-")))
        fecha_fin = date(*map(int, fecha_fin.split("-")))

        date_range = [
            fecha_inicio + timedelta(days=x)
            for x in range((fecha_fin - fecha_inicio).days + 1)
        ]

        date_range = [date.strftime(fecha, "%d/%m/%Y") for fecha in date_range]

        i = 0

        for l in range(len(procedures)):
            try:
                if procedures[i]["created_at"].split(" ")[0] not in date_range:
                    procedures.pop(i)
                else:
                    i += 1
            except IndexError:
                break

    elif fecha_fin != None and fecha_inicio != None and year == None:
        fecha_inicio = date(*map(int, fecha_inicio.split("-")))
        fecha_fin = date(*map(int, fecha_fin.split("-")))

        date_range = [
            fecha_inicio + timedelta(days=x)
            for x in range((fecha_fin - fecha_inicio).days + 1)
        ]

        date_range = [date.strftime(fecha, "%d/%m/%Y") for fecha in date_range]

        for l in range(len(procedures)):
            try:
                if procedures[i]["created_at"].split(" ")[0] not in date_range:
                    procedures.pop(i)
                else:
                    i += 1
            except IndexError:
                break
    data = {
        "usuario": nombreUsuario,
        "area_usuaria": area.nombre,
        "creacion": creacion,
        "procedures": procedures,
        "name": "tramites",
    }

    path = get_procedure_data_xlsx(data)
    return Response({"path": path}, status=status.HTTP_200_OK)


# modificaciones de api
@api_view(["POST"])
def get_reporte_matricula_pdf(request):
    if request.method == "POST":
        return api_get_reporte_matricula_pdf(request)


@api_view(["GET"])
def get_listado_alumnos_excel(request):
    if request.method == "GET":
        return api_get_listado_alumnos_excel(request)


@api_view(["POST"])
def get_reporte_actanotas_pdf(request):
    if request.method == "POST":
        return api_get_reporte_actanotas_pdf(request)


@api_view(["POST"])
def get_reporte_actanotas_aplazado_pdf(request):
    if request.method == "POST":
        return api_get_reporte_actanotas_aplazado_pdf(request)


@api_view(["POST"])
def get_reporte_academico_alumno_pdf(request):
    if request.method == "POST":
        return api_get_reporte_academico_alumno_pdf(request)


@api_view(["POST"])
def get_reporte_economico_alumno_pdf(request):
    if request.method == "POST":
        return api_get_reporte_economico_alumno_pdf(request)


@api_view(["GET"])
def get_reporte_pensiones_programas_excel(request):
    if request.method == "GET":
        return api_get_reporte_pensiones_programas_excel(request)


@api_view(["GET"])
def get_reporte_programas_excel(request):
    if request.method == "GET":
        return api_get_reporte_programas_excel(request)


@api_view(["GET"])
def generate_diploma_pdf(request):
    if request.method == "GET":
        return api_generate_diploma_pdf(request)
