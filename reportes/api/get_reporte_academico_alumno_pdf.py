from rest_framework.response import Response
from rest_framework import status
from django.template.loader import render_to_string
from weasyprint import HTML
import os
import time
from backend import settings
from django.db.models import Max, Min
import datetime
from academicos.models import Matricula, Cursos
from admision.models import Expediente
from core.models import CargoArea, Etapa
from reportes.functions import funtion_upload_file_to_s3
from decimal import Decimal, ROUND_HALF_UP


def api_get_reporte_academico_alumno_pdf(request):
    try:
        expediente_id = request.data.get("expediente_id")
        academico = reporte_academico_function(expediente_id)
        #
        html_string = render_to_string("reports/reporte-academico.html", academico)
        html = HTML(string=html_string)
        milisecond = str(int(round(time.time() * 1000)))
        folder_name = "pdf/academico/"
        pdf_file_name = "reporte-academico-{}-{}.pdf".format(expediente_id, milisecond)
        if settings.DEBUG:
            pdf_folder = os.path.join(settings.MEDIA_ROOT, folder_name)
            if not os.path.exists(pdf_folder):
                os.makedirs(pdf_folder)
            pdf_file_path = os.path.join(
                pdf_folder,
                "reporte-academico-{}-{}.pdf".format(expediente_id, milisecond),
            )
            html.write_pdf(target=pdf_file_path)
        else:
            html.write_pdf(target=pdf_file_name)

        path_return = funtion_upload_file_to_s3(pdf_file_name, folder_name)
        return Response({"path": path_return})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
    fecha_inicio = (
        obj_ejecucion.aggregate(Min("curso_grupo__fecha_inicio"))[
            "curso_grupo__fecha_inicio__min"
        ].strftime("%d/%m/%Y")
        if obj_ejecucion
        else ""
    )
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
           
            
            promedio_graduado = Decimal(notas_total) / creditos_total
            promedio_graduado = promedio_graduado.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
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

        if p.curso_grupo.grupo == "DI":
            modalidad = "EXAMEN DE SUFICIENCIA"
            ejecutado = f'{p.curso_grupo.fecha_inicio.strftime("%d/%m/%Y")}'
        else:
            modalidad = "EXTRACURRICULAR"
            ejecutado = f'{p.curso_grupo.fecha_inicio.strftime("%d/%m/%Y")} AL {p.curso_grupo.fecha_termino.strftime("%d/%m/%Y")}'
        cursos_extracurricular.append(
            {
                "curso": p.curso_grupo.curso.nombre,
                "modalidad": modalidad,
                "resolucion": p.curso_grupo.resolucion or "",
                "ejecutado": ejecutado,
                "nota": promedio_final,
                "docente": p.curso_grupo.docente.persona.get_full_name(),
                "acta": num_acta_extracurricular,
            }
        )
    # ENCARGADO OFICINA
    obj_cargoarea = CargoArea.objects.filter(
        cargo__id=1, is_active=True, area__id=1
    ).first()
    area = obj_cargoarea.area.first().nombre
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
        "area": area,
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
