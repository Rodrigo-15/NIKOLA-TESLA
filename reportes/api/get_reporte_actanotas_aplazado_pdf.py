from rest_framework.response import Response
from rest_framework import status
from django.template.loader import render_to_string
from weasyprint import HTML
import os
import time
from backend import settings
import datetime
from academicos.models import Matricula, Periodo, Aplazado
from admision.models import Expediente
from reportes.functions import funtion_upload_file_to_s3


def api_get_reporte_actanotas_aplazado_pdf(request):
    try:
        aplazado_id = request.data.get("aplazado_id")
        # cursogrupo_id = request.data.get("cursogrupo_id")
        periodo_id = request.data.get("periodo_id")
        actanotas = reporte_acta_aplazado_function(aplazado_id, periodo_id)
        #
        html_string = render_to_string(
            "reports/reporte-actanotas-aplazado.html", actanotas
        )
        html = HTML(string=html_string)
        milisecond = str(int(round(time.time() * 1000)))

        folder_name = "pdf/aplazados/"
        pdf_file_name = "reporte-actanotas-aplazado-{}-{}.pdf".format(
            aplazado_id, milisecond
        )
        if settings.DEBUG:
            pdf_folder = os.path.join(settings.MEDIA_ROOT, folder_name)
            if not os.path.exists(pdf_folder):
                os.makedirs(pdf_folder)
            pdf_file_path = os.path.join(
                pdf_folder,
                "reporte-actanotas-aplazado-{}-{}.pdf".format(aplazado_id, milisecond),
            )
            html.write_pdf(target=pdf_file_path)
        else:
            html.write_pdf(target=pdf_file_name)

        path_return = funtion_upload_file_to_s3(pdf_file_name, folder_name)
        return Response({"path": path_return})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def reporte_acta_aplazado_function(aplazado_id, periodo_id):
    periodo = Periodo.objects.get(id=periodo_id)
    cursogrupo = Matricula.objects.filter(aplazado_id=aplazado_id).first().curso_grupo
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
    matriculas = Matricula.get_curso_grupo_aplazado_by_id(aplazado_id)
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
    grupo_id = str(aplazado_id).rjust(5, "0")
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
