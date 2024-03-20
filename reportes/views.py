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
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.template.defaulttags import register
from django.shortcuts import render
from academicos.models import Matricula, Programa, PlanEstudio
from academicos.serializers import CursosSerializer, MatriculaSerializer
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


def DefaultTemplate(request):
    return render(request, "index.html")


@register.filter
def subtract(value, arg):
    value = float(value) - float(arg)
    return value


@register.simple_tag
def define_variable(value):
    return value


def reporte_matricula_alumno(request):
    expediente_id = 3407
    periodo_id = 1
    #
    expediente = reporte_matricula_alumno_function(expediente_id, periodo_id)
    return render(request, "reports/reporte-matricula.html", expediente)


def reporte_economico_alumno(request):
    expediente = Expediente.objects.filter(persona__numero_documento="73134712").first()
    # COSTO TOTAL PENSION
    if not expediente:
        return Response(
            {
                "error": "No se encontró el expediente para el alumno con número de documento {}".format(
                    73134712
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
    pagos_programa = pagos.filter(concepto__programa=expediente.programa)
    cantidad_pagos_programa = pagos_programa.count()
    suma_pagos_programa = pagos_programa.aggregate(Sum("monto"))["monto__sum"] or 0
    # PAGOS DE MATRICULA
    pagos_matricula = pagos.filter(concepto__id=concepto_matricula_id)
    cantidad_pagos_matricula = pagos_matricula.count()
    suma_pagos_matricula = pagos_matricula.aggregate(Sum("monto"))["monto__sum"] or 0
    # PAGOS DE OTROS CONCEPTOS
    pagos_otros = pagos.exclude(concepto__id=concepto_matricula_id).exclude(
        concepto__programa=expediente.programa
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
                "monto_cuota": str(pago.concepto.precio).replace(",", "."),
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
        monto_pagado = pago.monto + pago_anterior
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
        total_pago_matricula_lista += pago.monto
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
                "monto_cuota": str(pago.concepto.precio).replace(",", "."),
            }
        )
        total_pago_otros_lista += pago.monto

    return render(
        request,
        "reports/reporte-economico.html",
        {
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
        },
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
def get_reporte_programas_excel(request):
    # Type,Date = request.GET.get('dataFetch').split(':')
    programa_id = request.GET.get("programa_id")
    promocion = request.GET.get("promocion")
    anio = request.GET.get("anio")
    mes = request.GET.get("mes")
    dia = request.GET.get("dia")
    # path

    milisecond = str(int(round(time.time() * 1000)))
    media_root = settings.MEDIA_ROOT
    excel_folder = os.path.join(media_root, "economicos")
    if not os.path.exists(excel_folder):
        os.makedirs(excel_folder)
    excel_file_name = os.path.join(
        excel_folder,
        "reporte-programa-{}-{}-{}-{}-{}.xlsx".format(
            programa_id, anio, mes, dia, milisecond
        ),
    )
    if os.path.exists(excel_file_name):
        os.remove(excel_file_name)

    # EXCEL
    workbook = Workbook(excel_file_name)
    worksheet = workbook.add_worksheet()
    # formatFecha=workbook.add_format({'num_format': 'dd/mm/yyyy'})
    # formatMoney=workbook.add_format({'num_format': '#,##0'})
    # worksheet.set_column(2,2,cell_format=formatFecha)
    # worksheet.set_column(3,3,cell_format=formatMoney)
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
    worksheet.merge_range("A{}:E{}".format(linea, linea), " MONTO TOTAL", merge_format)
    worksheet.merge_range("F{}:I{}".format(linea, linea), monto_total, merge_format)
    workbook.close()

    # return
    path_return = os.path.join(
        settings.MEDIA_URL,
        "economicos",
        "reporte-programa-{}-{}-{}-{}-{}.xlsx".format(
            programa_id, anio, mes, dia, milisecond
        ),
    )
    path_return = path_return.replace("\\", "/")
    return Response({"path": path_return, "cantidad": len(Pagos_data)})


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
def get_reporte_matricula_pdf(request):
    expediente_id = request.GET.get("expediente")
    periodo_id = request.GET.get("periodo")
    expediente = reporte_matricula_alumno_function(expediente_id, periodo_id)
    print(expediente)
    #
    media_root = settings.MEDIA_ROOT
    pdf_folder = os.path.join(media_root, "pdf")
    if not os.path.exists(pdf_folder):
        os.makedirs(pdf_folder)
    #
    html_string = render_to_string("reports/reporte-matricula.html", expediente)
    html = HTML(string=html_string)
    milisecond = str(int(round(time.time() * 1000)))
    pdf_file_name = os.path.join(
        pdf_folder, "reporte-matricula-{}-{}.pdf".format(expediente_id, milisecond)
    )
    if os.path.exists(pdf_file_name):
        os.remove(pdf_file_name)
    html.write_pdf(target=pdf_file_name)
    #
    # from core.utils.email import send_mail
    # print("Enviando correo!!")
    # send_mail(expediente["expediente"]["correo_persona"], pdf_file_name)
    #
    path_return = os.path.join(
        settings.MEDIA_URL,
        "pdf",
        "reporte-matricula-{}-{}.pdf".format(expediente_id, milisecond),
    )
    path_return = path_return.replace("\\", "/")
    return Response({"path": path_return})


def reporte_matricula_alumno_function(expediente_id, periodo_id):
    #
    periodo = Periodo.objects.get(id=periodo_id)
    #
    expendiente = Expediente.objects.get(id=expediente_id)
    apellidos = (
        expendiente.persona.apellido_paterno
        + " "
        + expendiente.persona.apellido_materno
    )
    nombres = expendiente.persona.nombres
    numero_documento = expendiente.persona.numero_documento
    correo = expendiente.persona.correo
    num_expediente = expediente_id
    promocion = expendiente.promocion
    #
    programa = Programa.objects.get(id=expendiente.programa.id)
    programa_nombre = programa.nombre
    #
    matriculas = Matricula.objects.filter(
        expediente=expediente_id, periodo=periodo_id, is_retirado=False
    ).order_by("curso_grupo__curso__codigo")
    cursos = []
    for matricula in matriculas:
        curso = Cursos.objects.get(id=matricula.curso_grupo.curso.id)
        grupo = matricula.curso_grupo.grupo
        cursos.append({"curso": curso, "grupo": grupo})

    # FECHA DE REPORTE
    fecha_matricula = matriculas.first().fecha
    dia = fecha_matricula.day
    anio = fecha_matricula.year
    mes_id = fecha_matricula.strftime("%m")
    mes_array = [
        {"nombre": "Enero"},
        {"nombre": "Febrero"},
        {"nombre": "Marzo"},
        {"nombre": "Abril"},
        {"nombre": "Mayo"},
        {"nombre": "Junio"},
        {"nombre": "Julio"},
        {"nombre": "Agosto"},
        {"nombre": "Septiembre"},
        {"nombre": "Octubre"},
        {"nombre": "Noviembre"},
        {"nombre": "Diciembre"},
    ]
    mes_name = mes_array[int(mes_id) - 1].get("nombre")
    fecha_actual_str = f"{dia} de {mes_name} de {anio}"

    return {
        "expediente": {
            "periodo": periodo,
            "apellidos": apellidos,
            "nombres": nombres,
            "numero_documento": numero_documento,
            "correo": correo,
            "num_expediente": num_expediente,
            "promocion": promocion,
            "programa_nombre": programa_nombre,
            "cursos": cursos,
            "fecha_actual_str": fecha_actual_str,
            "correo_persona": expendiente.persona.correo,
        }
    }


@api_view(["POST"])
def get_reporte_actanotas_pdf(request):
    cursogrupo_id = request.data.get("curso_grupo_id")
    periodo_id = request.data.get("periodo_id")
    actanotas = reporte_acta_function(cursogrupo_id, periodo_id)
    #
    media_root = settings.MEDIA_ROOT
    pdf_folder = os.path.join(media_root, "pdf")
    if not os.path.exists(pdf_folder):
        os.makedirs(pdf_folder)
    #
    html_string = render_to_string("reports/reporte-actanotas.html", actanotas)
    html = HTML(string=html_string)
    milisecond = str(int(round(time.time() * 1000)))
    pdf_file_name = os.path.join(
        pdf_folder, "reporte-actanotas-{}-{}.pdf".format(cursogrupo_id, milisecond)
    )
    if os.path.exists(pdf_file_name):
        os.remove(pdf_file_name)
    html.write_pdf(target=pdf_file_name)
    path_return = os.path.join(
        settings.MEDIA_URL,
        "pdf",
        "reporte-actanotas-{}-{}.pdf".format(cursogrupo_id, milisecond),
    )
    path_return = path_return.replace("\\", "/")
    return Response({"path": path_return})


def reporte_acta_function(cursogrupo_id, periodo_id):
    periodo = Periodo.objects.get(id=periodo_id)
    #
    cursogrupo = CursoGrupo.objects.get(id=cursogrupo_id)
    #
    cursonombre = cursogrupo.curso.nombre
    creditos = cursogrupo.curso.creditos
    grupo = cursogrupo.grupo
    fecha_inicio = cursogrupo.fecha_inicio
    fecha_termino = cursogrupo.fecha_termino
    resolucion = cursogrupo.resolucion
    docentenombre = cursogrupo.docente.persona.nombres
    docenteapellidos = (
        cursogrupo.docente.persona.apellido_paterno
        + " "
        + cursogrupo.docente.persona.apellido_materno
    )
    #
    programa = (
        cursogrupo.curso.plan_estudio.programa.nombre
        if cursogrupo.curso.plan_estudio.programa
        else "EXTRACURRICULAR"
    )
    #
    matriculas = Matricula.get_curso_grupo_by_id(cursogrupo_id)
    expedientes = []
    for matricula in matriculas:
        obj_expediente = {
            "expediente_id": matricula.expediente.id,
            "promedio_final": matricula.promedio_final,
        }

        expedientes.append(obj_expediente)
    alumnos = []
    num_orden = 0
    numeros_letras = [
        {"nombre": "Cero"},
        {"nombre": "Uno"},
        {"nombre": "Dos"},
        {"nombre": "Tres"},
        {"nombre": "Cuatro"},
        {"nombre": "Cinco"},
        {"nombre": "Seis"},
        {"nombre": "Siete"},
        {"nombre": "Ocho"},
        {"nombre": "Nueve"},
        {"nombre": "Diez"},
        {"nombre": "Once"},
        {"nombre": "Doce"},
        {"nombre": "Trece"},
        {"nombre": "Catorce"},
        {"nombre": "Quince"},
        {"nombre": "Dieciseis"},
        {"nombre": "Diecisiete"},
        {"nombre": "Dieciocho"},
        {"nombre": "Diecinueve"},
        {"nombre": "Veinte"},
    ]
    for expediente in expedientes:
        num_orden += 1
        alumno = Expediente.get_alumno_by_expediente_id(expediente["expediente_id"])
        promedio_final = expediente["promedio_final"]
        promedio_letra = numeros_letras[int(promedio_final)].get("nombre")
        alumnos.append(
            {
                "alumno": alumno,
                "promedio_final": promedio_final,
                "num_orden": num_orden,
                "promedio_letra": promedio_letra,
            }
        )

    dia = datetime.datetime.now().day
    anio = datetime.datetime.now().year
    #
    mes_id = datetime.datetime.now().strftime("%m")
    mes_array = [
        {"nombre": "Enero"},
        {"nombre": "Febrero"},
        {"nombre": "Marzo"},
        {"nombre": "Abril"},
        {"nombre": "Mayo"},
        {"nombre": "Junio"},
        {"nombre": "Julio"},
        {"nombre": "Agosto"},
        {"nombre": "Septiembre"},
        {"nombre": "Octubre"},
        {"nombre": "Noviembre"},
        {"nombre": "Diciembre"},
    ]
    mes_name = mes_array[int(mes_id) - 1].get("nombre")
    fecha_actual_str = f"{dia} de {mes_name} de {anio}"
    grupo_id = str(cursogrupo_id).rjust(5, "0")
    return {
        "actanotas": {
            "cursogrupo_id": grupo_id,
            "periodo": periodo,
            "cursonombre": cursonombre,
            "creditos": creditos,
            "docentenombre": docentenombre,
            "docenteapellidos": docenteapellidos,
            "programa_nombre": programa,
            "grupo": grupo,
            "alumnos": alumnos,
            "fecha_inicio": fecha_inicio,
            "fecha_termino": fecha_termino,
            "resolucion": resolucion,
            "fecha_actual_str": fecha_actual_str,
        }
    }


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


@api_view(["POST"])
def get_reporte_economico_alumno_pdf(request):
    if request.method == "POST":
        numero_documento = request.data.get("numero_documento")
        economicos = reporte_economico_function(numero_documento)
        # media
        media_root = settings.MEDIA_ROOT
        pdf_folder = os.path.join(media_root, "pdf")
        if not os.path.exists(pdf_folder):
            os.makedirs(pdf_folder)
        #
        html_string = render_to_string("reports/reporte-economico.html", economicos)
        html = HTML(string=html_string)
        milisecond = str(int(round(time.time() * 1000)))
        pdf_file_name = os.path.join(
            pdf_folder,
            "reporte-economico-{}-{}.pdf".format(numero_documento, milisecond),
        )
        if os.path.exists(pdf_file_name):
            os.remove(pdf_file_name)
        html.write_pdf(target=pdf_file_name)
        # from core.utils.email import send_mail
        # print("Enviando correo!!")
        # send_mail(expediente["expediente"]["correo_persona"], pdf_file_name)
        #
        # print("Termino de nvia correo!!")
        path_return = os.path.join(
            settings.MEDIA_URL,
            "pdf",
            "reporte-economico-{}-{}.pdf".format(numero_documento, milisecond),
        )
        path_return = path_return.replace("\\", "/")
        return Response({"path": path_return})


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
        area__id=5, cargo__id=5, is_active=True
    ).first()
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
        "anio": anio,
    }


@api_view(["POST"])
def get_reporte_academico_alumno_pdf(request):
    if request.method == "POST":
        expediente_id = request.data.get("expediente_id")
        academico = reporte_academico_function(expediente_id)
        # media
        media_root = settings.MEDIA_ROOT
        pdf_folder = os.path.join(media_root, "pdf")
        if not os.path.exists(pdf_folder):
            os.makedirs(pdf_folder)
        #
        html_string = render_to_string("reports/reporte-academico.html", academico)
        html = HTML(string=html_string)
        milisecond = str(int(round(time.time() * 1000)))
        pdf_file_name = os.path.join(
            pdf_folder, "reporte-academico-{}-{}.pdf".format(expediente_id, milisecond)
        )
        if os.path.exists(pdf_file_name):
            os.remove(pdf_file_name)

        html.write_pdf(target=pdf_file_name)
        path_return = os.path.join(
            settings.MEDIA_URL,
            "pdf",
            "reporte-academico-{}-{}.pdf".format(expediente_id, milisecond),
        )
        path_return = path_return.replace("\\", "/")
        return Response({"path": path_return})


def reporte_academico_function(expediente_id):
    # DATOS DE EXPEDIENTE
    expediente = Expediente.objects.filter(id=expediente_id).first()
    # fecha ejecucion y condicion
    obj_ejecucion = (
        Matricula.objects.filter(expediente_id=expediente_id, is_retirado=False)
        .exclude(curso_grupo__curso__plan_estudio__programa__isnull=True)
        .values("curso_grupo__fecha_inicio", "curso_grupo__fecha_termino")
    )
    etapas = Etapa.objects.filter(
        promocion=expediente.promocion, programa_id=expediente.programa.id
    )
    fecha_inicio = obj_ejecucion.aggregate(Min("curso_grupo__fecha_inicio"))[
        "curso_grupo__fecha_inicio__min"
    ].strftime("%d/%m/%Y")
    fecha_final = ""
    condicion = "ESTUDIANTE"
    if expediente.is_graduate == True:
        fecha_final = obj_ejecucion.aggregate(Max("curso_grupo__fecha_termino"))[
            "curso_grupo__fecha_termino__max"
        ].strftime("%d/%m/%Y")
        condicion = "EGRESADO"
    fecha_1_mat = (
        etapas.aggregate(Min("fecha_inicio"))["fecha_inicio__min"].strftime("%d/%m/%Y")
        if etapas
        else ""
    )
    # DATOS CURSOS
    obj_curso = Cursos.objects.filter(
        plan_estudio__programa__id=expediente.programa.id
    ).order_by("id")
    cursos = []
    total_creditos = 0
    for curso in obj_curso:
        obj_nota = (
            Matricula.objects.filter(
                curso_grupo__curso_id=curso.id,
                expediente_id=expediente_id,
                is_retirado=False,
            )
            .order_by("-promedio_final")
            .first()
        )
        if obj_nota != None:
            num_acta = str(obj_nota.curso_grupo.id).zfill(6)
            periodo = obj_nota.curso_grupo.periodo.nombre
            resolucion = obj_nota.curso_grupo.resolucion or ""
            if obj_nota.is_old == False and obj_nota.is_aplazado == True:
                nota = obj_nota.promedio_final_aplazado or ""
                num_acta = f"{str(obj_nota.curso_grupo.id).zfill(6)}-A{obj_nota.aplazado.num_acta}"
                det_acta = "APLAZADO"
            elif obj_nota.is_old == False and obj_nota.is_dirigido == True:
                nota = obj_nota.promedio_final
                det_acta = "DIRIGIDO"
            elif obj_nota.is_old == True and obj_nota.is_dirigido == True:
                nota = obj_nota.promedio_final
                det_acta = "DIRIGIDO"
                num_acta = obj_nota.num_acta_ref
            elif obj_nota.is_old == True and obj_nota.is_aplazado == True:
                nota = obj_nota.promedio_final_aplazado or ""
                det_acta = "APLAZADO"
                num_acta = obj_nota.aplazado.num_acta
            elif obj_nota.is_old == True:
                nota = obj_nota.promedio_final
                det_acta = "REGULAR"
                num_acta = obj_nota.num_acta_ref
            elif obj_nota.is_convalidado == True:
                nota = obj_nota.promedio_final
                det_acta = "CONVALIDADO"
                num_acta = "-"
                periodo = "-"
                resolucion = "-"
            elif obj_nota.is_cerrado == True:
                nota = obj_nota.promedio_final
                det_acta = "REGULAR"
            else:
                nota = ""
                num_acta = ""
                det_acta = ""
                periodo = ""
                resolucion = ""
        else:
            nota = ""
            num_acta = ""
            det_acta = ""
            periodo = ""
            resolucion = ""
        cursos.append(
            {
                "nombre": curso.nombre,
                "creditos": curso.creditos,
                "ciclo": roman_number(curso.ciclo),
                "nota": nota,
                "num_acta": num_acta,
                "det_acta": det_acta,
                "periodo": periodo,
                "resolucion": resolucion,
            }
        )
        total_creditos = total_creditos + curso.creditos
    # FECHA DE REPORTE
    dia = datetime.datetime.now().day
    anio = datetime.datetime.now().year
    mes_id = datetime.datetime.now().strftime("%m")
    mes_array = [
        {"nombre": "Enero"},
        {"nombre": "Febrero"},
        {"nombre": "Marzo"},
        {"nombre": "Abril"},
        {"nombre": "Mayo"},
        {"nombre": "Junio"},
        {"nombre": "Julio"},
        {"nombre": "Agosto"},
        {"nombre": "Septiembre"},
        {"nombre": "Octubre"},
        {"nombre": "Noviembre"},
        {"nombre": "Diciembre"},
    ]
    mes_name = mes_array[int(mes_id) - 1].get("nombre")
    fecha_actual_str = f"{dia} de {mes_name} de {anio}"
    # PPS Y PPG
    obj_periodo = Matricula.objects.filter(expediente_id=expediente_id).distinct(
        "periodo_id"
    )
    promedios_x_ciclo = []
    promedio_graduado = "-"
    notas_total = 0
    creditos_total = 0
    creditos_aprobados = 0
    for periodo in obj_periodo:
        obj_nota = Matricula.objects.filter(
            expediente_id=expediente_id,
            periodo_id=periodo.periodo.id,
            is_retirado=False,
            is_cerrado=True,
            curso_grupo__curso__plan_estudio__programa__isnull=False,
        ).order_by("curso_grupo__curso__codigo")
        ppc = 0
        creditos = 0
        for p in obj_nota:
            if p.is_aplazado == True:
                if p.promedio_final_aplazado == None:
                    promedio_final = p.promedio_final
                else:
                    promedio_final = p.promedio_final_aplazado
            else:
                promedio_final = p.promedio_final

            ppc += promedio_final * p.curso_grupo.curso.creditos
            creditos += p.curso_grupo.curso.creditos
            if (
                promedio_final >= 14
                and p.curso_grupo.curso.plan_estudio.programa.tipo_id in [1, 3]
            ):
                creditos_aprobados += p.curso_grupo.curso.creditos
            if (
                promedio_final >= 15
                and p.curso_grupo.curso.plan_estudio.programa.tipo_id == 2
            ):
                creditos_aprobados += p.curso_grupo.curso.creditos
        notas_total += ppc
        creditos_total += creditos
        if len(obj_nota) > 0:
            promedios_x_ciclo.append(
                {
                    "periodo": periodo.periodo.nombre,
                    "promedio": round((ppc / creditos), 2),
                }
            )
            promedio_graduado = round((notas_total / creditos_total), 2)
        else:
            promedios_x_ciclo.append(
                {
                    "periodo": "-",
                    "promedio": "-",
                }
            )

    # EXTRACURRICULARES
    obj_extracurricular = Matricula.objects.filter(
        expediente_id=expediente_id,
        periodo_id=periodo.periodo.id,
        is_retirado=False,
        is_cerrado=True,
        curso_grupo__curso__plan_estudio__programa__isnull=True,
    ).order_by("curso_grupo__curso__codigo")
    cursos_extracurricular = []
    for p in obj_extracurricular:
        if p.is_aplazado == True:
            if p.promedio_final_aplazado == None:
                promedio_final = p.promedio_final
            else:
                promedio_final = p.promedio_final_aplazado
        else:
            promedio_final = p.promedio_final

        if p.is_old == True:
            num_acta_extracurricular = p.num_acta_ref
        else:
            num_acta_extracurricular = str(p.curso_grupo.id).zfill(6)
        cursos_extracurricular.append(
            {
                "curso": p.curso_grupo.curso.nombre,
                "modalidad": "EXTRACURRICULAR",
                "resolucion": p.curso_grupo.resolucion or "",
                "ejecutado": f'{p.curso_grupo.fecha_inicio.strftime("%d/%m/%Y")} AL {p.curso_grupo.fecha_termino.strftime("%d/%m/%Y")}',
                "nota": promedio_final,
                "docente": p.curso_grupo.docente.persona.get_full_name(),
                "acta": num_acta_extracurricular,
            }
        )

    # ENCARGADO OFICINA
    obj_cargoarea = CargoArea.objects.filter(
        area__id=1, cargo__id=1, is_active=True
    ).first()

    #
    return {
        "expediente": expediente,
        "cursos": cursos,
        "cursos_extracurricular": cursos_extracurricular,
        "promedios_x_ciclo": promedios_x_ciclo,
        "promedio_graduado": promedio_graduado,
        "total_creditos": total_creditos,
        "creditos_aprobados": creditos_aprobados,
        "fecha_inicio": fecha_inicio,
        "fecha_final": fecha_final,
        "condicion": condicion,
        "fecha_actual": fecha_actual_str,
        "fecha_1_mat": fecha_1_mat,
        "cargoarea": obj_cargoarea,
        "anio": anio,
    }


def roman_number(number):
    num = [1, 4, 5, 9, 10, 40, 50, 90, 100, 400, 500, 900, 1000]
    sym = ["I", "IV", "V", "IX", "X", "XL", "L", "XC", "C", "CD", "D", "CM", "M"]
    romano = []
    i = 12
    valor = number
    while valor:
        div = valor // num[i]
        valor %= num[i]
        while div:
            romano.append(sym[i])
            div -= 1
        i -= 1

    return "".join(romano)


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

    url = URL_LOCAL if DEBUG else URL_PROD
    path = path.replace("/media", "media")
    path = url + path
    return Response({"path": path}, status=status.HTTP_200_OK)


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


@api_view(["POST"])
def get_reporte_actanotas_aplazado_pdf(request):
    aplazado_id = request.data.get("aplazado_id")
    cursogrupo_id = request.data.get("cursogrupo_id")
    periodo_id = request.data.get("periodo_id")
    actanotas = reporte_acta_aplazado_function(cursogrupo_id, aplazado_id, periodo_id)
    #
    media_root = settings.MEDIA_ROOT
    pdf_folder = os.path.join(media_root, "pdf")
    if not os.path.exists(pdf_folder):
        os.makedirs(pdf_folder)
    #
    html_string = render_to_string("reports/reporte-actanotas-aplazado.html", actanotas)
    html = HTML(string=html_string)
    milisecond = str(int(round(time.time() * 1000)))
    pdf_file_name = os.path.join(
        pdf_folder,
        "reporte-actanotas-aplazado-{}-{}-{}.pdf".format(
            cursogrupo_id, aplazado_id, milisecond
        ),
    )
    if os.path.exists(pdf_file_name):
        os.remove(pdf_file_name)
    html.write_pdf(target=pdf_file_name)
    path_return = os.path.join(
        settings.MEDIA_URL,
        "pdf",
        "reporte-actanotas-aplazado-{}-{}-{}.pdf".format(
            cursogrupo_id, aplazado_id, milisecond
        ),
    )
    path_return = path_return.replace("\\", "/")
    return Response({"path": path_return})


def reporte_acta_aplazado_function(cursogrupo_id, aplazado_id, periodo_id):
    periodo = Periodo.objects.get(id=periodo_id)
    cursogrupo = CursoGrupo.objects.get(id=cursogrupo_id)
    aplazado = Aplazado.objects.get(id=aplazado_id)
    #
    cursonombre = cursogrupo.curso.nombre
    creditos = cursogrupo.curso.creditos
    grupo = cursogrupo.grupo

    # aplazado
    fecha = aplazado.fecha
    resolucion = aplazado.resolucion
    docentenombre = aplazado.docente.persona.nombres
    docenteapellidos = (
        aplazado.docente.persona.apellido_paterno
        + " "
        + aplazado.docente.persona.apellido_materno
    )
    num_acta = aplazado.num_acta
    #

    programa = cursogrupo.curso.plan_estudio.programa.nombre
    #
    matriculas = Matricula.get_curso_grupo_aplazado_by_id(cursogrupo_id, aplazado_id)
    expedientes = []
    for matricula in matriculas:
        obj_expediente = {
            "expediente_id": matricula.expediente.id,
            "promedio_final": matricula.promedio_final_aplazado,
        }

        expedientes.append(obj_expediente)
    alumnos = []
    num_orden = 0
    numeros_letras = [
        {"nombre": "Cero"},
        {"nombre": "Uno"},
        {"nombre": "Dos"},
        {"nombre": "Tres"},
        {"nombre": "Cuatro"},
        {"nombre": "Cinco"},
        {"nombre": "Seis"},
        {"nombre": "Siete"},
        {"nombre": "Ocho"},
        {"nombre": "Nueve"},
        {"nombre": "Diez"},
        {"nombre": "Once"},
        {"nombre": "Doce"},
        {"nombre": "Trece"},
        {"nombre": "Catorce"},
        {"nombre": "Quince"},
        {"nombre": "Dieciseis"},
        {"nombre": "Diecisiete"},
        {"nombre": "Dieciocho"},
        {"nombre": "Diecinueve"},
        {"nombre": "Veinte"},
    ]
    for expediente in expedientes:
        num_orden += 1
        alumno = Expediente.get_alumno_by_expediente_id(expediente["expediente_id"])
        promedio_final = expediente["promedio_final"]
        promedio_letra = numeros_letras[int(promedio_final)].get("nombre")
        alumnos.append(
            {
                "alumno": alumno,
                "promedio_final": promedio_final,
                "num_orden": num_orden,
                "promedio_letra": promedio_letra,
            }
        )

    dia = datetime.datetime.now().day
    anio = datetime.datetime.now().year
    #
    mes_id = datetime.datetime.now().strftime("%m")
    mes_array = [
        {"nombre": "Enero"},
        {"nombre": "Febrero"},
        {"nombre": "Marzo"},
        {"nombre": "Abril"},
        {"nombre": "Mayo"},
        {"nombre": "Junio"},
        {"nombre": "Julio"},
        {"nombre": "Agosto"},
        {"nombre": "Septiembre"},
        {"nombre": "Octubre"},
        {"nombre": "Noviembre"},
        {"nombre": "Diciembre"},
    ]
    mes_name = mes_array[int(mes_id) - 1].get("nombre")
    fecha_actual_str = f"{dia} de {mes_name} de {anio}"
    grupo_id = str(cursogrupo_id).rjust(5, "0")
    return {
        "actanotas": {
            "cursogrupo_id": grupo_id,
            "periodo": periodo,
            "cursonombre": cursonombre,
            "creditos": creditos,
            "docentenombre": docentenombre,
            "docenteapellidos": docenteapellidos,
            "programa_nombre": programa,
            "grupo": grupo,
            "alumnos": alumnos,
            "fecha": fecha,
            "resolucion": resolucion,
            "num_acta": num_acta,
            "fecha_actual_str": fecha_actual_str,
        }
    }


@api_view(["GET"])
def get_reporte_pensiones_programas_excel(request):
    programa_id = request.GET.get("programa_id")
    promocion = request.GET.get("promocion")

    if programa_id == None:
        return Response(
            {"error": "No se encontro el programa"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # path
    milisecond = str(int(round(time.time() * 1000)))
    media_root = settings.MEDIA_ROOT
    excel_folder = os.path.join(media_root, "economicos")
    if not os.path.exists(excel_folder):
        os.makedirs(excel_folder)
    excel_file_name = os.path.join(
        excel_folder,
        "reporte-pensiones-programa-{}-{}-{}.xlsx".format(
            programa_id, promocion, milisecond
        ),
    )
    if os.path.exists(excel_file_name):
        os.remove(excel_file_name)

    # EXCEL
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

    # return
    path_return = os.path.join(
        settings.MEDIA_URL,
        "economicos",
        "reporte-pensiones-programa-{}-{}-{}.xlsx".format(
            programa_id, promocion, milisecond
        ),
    )
    path_return = path_return.replace("\\", "/")
    return Response({"path": path_return})


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


@api_view(["GET"])
def get_listado_alumnos_excel(request):
    cursogrupo_id = request.GET.get("cursogrupo_id")
    if cursogrupo_id == None:
        return Response(
            {"error": "No se encontro el curso"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # path
    milisecond = str(int(round(time.time() * 1000)))
    media_root = settings.MEDIA_ROOT
    excel_folder = os.path.join(media_root, "academicos")
    if not os.path.exists(excel_folder):
        os.makedirs(excel_folder)
    excel_file_name = os.path.join(
        excel_folder,
        "Lista-alumnos-curso-{}-{}.xlsx".format(cursogrupo_id, milisecond),
    )
    if os.path.exists(excel_file_name):
        os.remove(excel_file_name)

    # EXCEL
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

    # return
    path_return = os.path.join(
        settings.MEDIA_URL,
        "academicos",
        "Lista-alumnos-curso-{}-{}.xlsx".format(cursogrupo_id, milisecond),
    )
    path_return = path_return.replace("\\", "/")
    return Response({"path": path_return})


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


# new code
@api_view(["GET"])
def generate_diploma_pdf(request):
    if request.method == "GET":
        expediente_id = request.GET.get("expediente_id")
        if expediente_id == None:
            return Response(
                {"error": "No se encontro el expediente"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        expediente = Expediente.objects.filter(id=expediente_id).first()
        num_doc = expediente.persona.numero_documento
        persona = (
            expediente.persona.nombres
            + " "
            + expediente.persona.apellido_paterno
            + " "
            + expediente.persona.apellido_materno
        )
        nombres = expediente.persona.nombres
        apellidos = (
            expediente.persona.apellido_paterno
            + " "
            + expediente.persona.apellido_materno
        )
        programa = expediente.programa.nombre
        programa_id = expediente.programa

        data_matricula = Matricula.objects.filter(expediente=expediente_id)

        curso_grupo_ids = list(data_matricula.values_list("curso_grupo", flat=True))

        data_curso = CursoGrupo.objects.filter(id__in=curso_grupo_ids)

        docentes = list(set([curso.docente.full_name() for curso in data_curso]))
        cursos = [grupocurso.curso.nombre for grupocurso in data_curso]
        creditos = [grupocurso.curso.creditos for grupocurso in data_curso]
        notas = [matricula.promedio_final for matricula in data_matricula]

        curso_nota = []

        for i in range(len(cursos)):
            curso_nota.append([cursos[i], notas[i], creditos[i]])
        if expediente.programa.tipo.id == 3:
            data = {
                "num_doc": num_doc,
                "persona": persona,
                "nombres": nombres,
                "apellidos": apellidos,
                "programa": programa,
                "programa_id": programa_id,
                "fecha_inicio": expediente.periodo.fecha_inicio,
                "fecha_final": expediente.periodo.fecha_fin,
                "docentes": docentes,
                "cursos": curso_nota,
            }
            path_return = diploma_diplomado(data)
        else:
            data = {
                "num_doc": num_doc,
                "persona": persona,
                "nombres": nombres,
                "apellidos": apellidos,
                "programa": programa,
                "programa_id": programa_id,
            }
            path_return = diploma_egresado(data)
        return Response({"path": path_return})


@api_view(["GET"])
def get_tramites_pendientes_excel(request):
    user_id = request.GET.get("user_id")
    cargo_area = CargoArea.objects.filter(persona__user_id=user_id).first()

    area = cargo_area.area.first()

    if not area:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"message": "El usuario no tiene un area asignada"},
        )
    area = AreaSerializer(area).data

    area_id = area.get("id")
    area_nombre = area.get("nombre")

    tracings_for_user = ProcedureTracing.objects.filter(
        from_area=area_id, is_finished=False
    ).order_by("-created_at")

    procedures = []

    for tracing in tracings_for_user:
        procedure = ProcedureSerializer(tracing.procedure).data

        if procedure not in procedures:

            procedures.append(procedure)

    data = {"area_usuaria": area_nombre, "procedures": procedures}

    path = get_unfinished_procedures_for_area_xlsx(data)

    url = URL_LOCAL if DEBUG else URL_PROD
    path = path.replace("/media", "media")
    path = url + path
    return Response({"path": path}, status=status.HTTP_200_OK)


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
    data_area = cargo_area.area.all()
    areas = AreaSerializer(data_area, many=True).data
    fecha = datetime.datetime.now().strftime("%d/%m/%Y")
    hora = datetime.datetime.now().strftime("%H:%M %p")
    anio = datetime.datetime.now().year
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
        serialized_procedure["action"] = trackin.action
        obj_procedure.append(serialized_procedure)

    procedure_charge = ProcedureCharge.objects.filter(id=procedure_charge_id).first()

    text_charge_number = procedure_charge.correlative

    final_data = {
        "area": dict(areas[0]),
        "fecha": fecha,
        "hora": hora,
        "anio": anio,
        "usuario": PersonaSerializerFilter(usuario).data,
        "procedure": obj_procedure,
        "procedure_count": len(obj_procedure),
        "charge_number": text_charge_number,
    }
    path = get_charge_procedure(final_data)
    path = path.replace("/media", "media")
    return Response({"path": path}, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_traffic_in_area_excel(request):
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    user_id = request.GET.get("user_id")

    if user_id == None or fecha_inicio == None or fecha_fin == None:
        return Response(
            {"error": "No se encontro el area o las fechas"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cargo_area = CargoArea.objects.filter(persona__user_id=user_id).first()
    if not cargo_area:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"message": "El usuario no tiene un area asignada"},
        )

    area = AreaSerializer(cargo_area.area, many=True).data

    from backend.settings import DEBUG, URL_LOCAL, URL_PROD

    fecha_inicio = date(*map(int, fecha_inicio.split("-")))
    fecha_fin = date(*map(int, fecha_fin.split("-")))

    date_range = [
        fecha_inicio + timedelta(days=x)
        for x in range((fecha_fin - fecha_inicio).days + 1)
    ]
    tracingList = []

    for fecha in date_range:
        tracing_for_date = ProcedureTracingSerializer(
            ProcedureTracing.objects.filter(
                created_at__date=fecha, from_area__id=area[0]["id"]
            ),
            many=True,
        ).data

        tracingList.append(tracing_for_date)

    area_usuaria = area[0]

    for i in range(len(date_range)):
        date_range[i] = datetime.datetime.strftime(date_range[i], "%Y-%m-%d")

    path = generate_graph_traffic(tracingList, area_usuaria, date_range)

    url = URL_LOCAL if DEBUG else URL_PROD
    path = path.replace("/media", "media")
    path = url + path

    return Response({"path": path}, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_tramites_dentro_fuera_de_plazo(request):
    user_id = request.GET.get("user_id")

    if user_id == None:
        return Response(
            {"error": "No se encontro el area o las fechas"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cargo_area = CargoArea.objects.filter(persona__user_id=user_id).first()
    if not cargo_area:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"message": "El usuario no tiene un area asignada"},
        )

    area = AreaSerializer(cargo_area.area, many=True).data
    area = area[0]

    cargo_area = CargoArea.objects.filter(area__id=area["id"])

    trackins = []

    for value in cargo_area:
        trackins.append(ProcedureTracing(user__area_id=cargo_area.user_id))

    obj_procedure = []
    for trackin in trackins:
        procedure = Procedure.objects.filter(id=trackin.procedure_id).first()
        serialized_procedure = ProcedureSerializer(procedure).data
        to_area = Area.objects.filter(id=trackin.to_area_id).first()
        serialized_procedure["to_area"] = AreaSerializer(to_area).data
        serialized_procedure["action"] = trackin.action
        obj_procedure.append(serialized_procedure)

    procedureList = Procedure.objects.filter(user__area = area["id"])

    print(procedureList)

@api_view(["GET"])
def get_constancia_registro(request):
    procedure_id = request.GET.get("procedure_id")

    if procedure_id == None:
        return Response(
            {"error": "No se encontro  el procedure"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    procedure: Procedure = Procedure.objects.filter(id=procedure_id).first()

    procedureType = procedure.procedure_type.concepto

    fecha, hora = str(procedure.created_at).split(" ")

    persona = f"{procedure.file.person.nombres} {procedure.file.person.apellido_paterno} {procedure.file.person.apellido_materno}"

    dni = procedure.file.person.numero_documento

    data = [persona, dni, procedureType, fecha]

    path = generate_constancia_de_registro(data)
    path = path.replace("/media", "media")
    return Response({"path": path}, status=status.HTTP_200_OK)

@api_view(["GET"])
def get_tramites_area_excel(request):
    user_id = request.GET.get("user_id")
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    año = request.GET.get("año")
    state = request.GET.get("state")
    state_date = request.GET.get("state_date")

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

    area = (AreaSerializer(cargo_area.area, many=True).data)[0]

    tracings_for_user = ProcedureTracing.objects.filter(
        from_area=area["id"]).order_by("-created_at")

    procedures = []

    for tracing in tracings_for_user:
        procedure = ProcedureSerializer(tracing.procedure).data

        if procedure not in procedures:

            procedures.append(procedure)
    i = 0
    for l in range(len(procedures)):
        try:
            if state == None and state_date != None:
                if procedures[i]["state_date"] != state_date:
                    procedures.pop(i)
                else:
                    i+=1
            elif state != None and state_date == None:
                if procedures[i]["state"] != state:
                    procedures.pop(i)
                else:
                    i+=1
            elif state != None and state_date != None:
                if procedures[i]["state"] != state or procedures[i]["state_date"] != state_date:
                    procedures.pop(i)
                else:
                    i+=1
        except IndexError:
            break
    
    if fecha_fin == None and fecha_inicio == None and año == None:
        pass
    elif fecha_fin == None and fecha_inicio == None and año != None:
        fecha_inicio = f"{año}-01-01"
        fecha_fin = f"{año}-12-31"
        fecha_inicio = date(*map(int, fecha_inicio.split("-")))
        fecha_fin = date(*map(int, fecha_fin.split("-")))

        date_range = [
            fecha_inicio + timedelta(days=x)
            for x in range((fecha_fin - fecha_inicio).days + 1)
        ]

        i = 0
        for l in range(len(procedures)):
            try:
                if procedures[i]["created_at"] not in date_range:
                    procedures.pop(i)
                else:
                    i += 1
            except IndexError:
                break
    elif fecha_fin != None and fecha_inicio != None and año == None:
        fecha_inicio = date(*map(int, fecha_inicio.split("-")))
        fecha_fin = date(*map(int, fecha_fin.split("-")))

        date_range = [
            fecha_inicio + timedelta(days=x)
            for x in range((fecha_fin - fecha_inicio).days + 1)
        ]

        for l in range(len(procedures)):
            try:
                if procedures[i]["created_at"] not in date_range:
                    procedures.pop(i)
                else:
                    i += 1
            except IndexError:
                break

    data = {"area_usuaria": area["nombre"], "procedures": procedures}

    path = get_unfinished_procedures_for_area_xlsx(data)

    url = URL_LOCAL if DEBUG else URL_PROD
    path = path.replace("/media", "media")
    path = url + path
    return Response({"path": path}, status=status.HTTP_200_OK)