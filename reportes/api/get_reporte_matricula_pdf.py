from rest_framework.response import Response
from rest_framework import status
from django.template.loader import render_to_string
from weasyprint import HTML
import os
import time
from backend import settings
from academicos.models import Matricula, Periodo, Programa, Cursos
from admision.models import Expediente
from reportes.functions import funtion_upload_file_to_s3


def api_get_reporte_matricula_pdf(request):
    try:
        expediente_id = request.data.get("expediente")
        periodo_id = request.data.get("periodo")
        expediente = reporte_matricula_alumno_function(expediente_id, periodo_id)

        html_string = render_to_string("reports/reporte-matricula.html", expediente)
        html = HTML(string=html_string)
        milisecond = str(int(round(time.time() * 1000)))

        folder_name = "pdf/matriculas/"
        pdf_file_name = "reporte-matricula-{}-{}.pdf".format(expediente_id, milisecond)
        if settings.DEBUG:
            pdf_folder = os.path.join(settings.MEDIA_ROOT, folder_name)
            if not os.path.exists(pdf_folder):
                os.makedirs(pdf_folder)
            pdf_file_path = os.path.join(
                pdf_folder,
                "reporte-matricula-{}-{}.pdf".format(expediente_id, milisecond),
            )
            html.write_pdf(target=pdf_file_path)
        else:
            html.write_pdf(target=pdf_file_name)

        path_return = funtion_upload_file_to_s3(pdf_file_name, folder_name)
        return Response({"path": path_return})

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
