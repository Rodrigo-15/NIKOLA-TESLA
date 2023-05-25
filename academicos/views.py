from pickle import TRUE

from django.db.models import F, Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from academicos.models import (
    CursoGrupo,
    Cursos,
    Docente,
    Horario,
    Matricula,
    Programa,
    RequisitoCurso,
)
from academicos.serializers import (
    CursoGrupoSerializer,
    CursoMatriculaSerializer,
    ExpedienteDocenteserializer,
    MatriculaSerializer,
    ProgramaSerializer,
)
from admision.models import Expediente
from admision.serializers.expediente import (
    ExpedienteAlumnoSerializer,
    ExpedienteMatriculaSerializer,
    ExpedientePersonaSerializer,
    ExpedientesSerializer,
)
from core.models import Periodo, Persona
from core.serializers import PeridoExpedienteSerializer
from economicos.models import Concepto, Pago

# Create your views here.


@api_view(["GET"])
def get_alumno(request):
    if request.method == "GET":
        persona_id = request.GET.get("persona_id")
        alumno = Expediente.get_alumno_by_id_persona(persona_id)
        expedientes = Expediente.get_alumno_expedientes_by_id_persona(persona_id)
        if not alumno:
            return Response({"message": "Alumno no encontrado"}, status=404)
        serializer = ExpedientePersonaSerializer(alumno)
        serializer_expedientes = ExpedientesSerializer(expedientes, many=True)
        return Response({**serializer.data, "expedientes": serializer_expedientes.data})


@api_view(["GET"])
def get_cursos_by_programa_id(request):
    if request.method == "GET":
        programa_id = request.GET.get("programa_id")
        expediente_id = request.GET.get("expediente_id")
        # Pagos de expedientes
        obj_programa = (
            Programa.objects.filter(id=programa_id)
            .values("codigo", "cuotas", "costo")
            .first()
        )
        obj_pago_ciclo = (
            Matricula.objects.filter(expediente_id=expediente_id)
            .distinct("curso_grupo__curso__ciclo")
            .values("curso_grupo__curso__ciclo")
            .order_by("-curso_grupo__curso__ciclo")
            .first()
        )
        if obj_pago_ciclo == None:
            pago_ciclo = 0
        else:
            pago_ciclo = obj_pago_ciclo["curso_grupo__curso__ciclo"]
        obj_pagos = Pago.objects.filter(
            expendiente_id=expediente_id,
            concepto__programa__codigo=obj_programa["codigo"],
        )
        monto_total = 0
        for pago in obj_pagos:
            monto_total = monto_total + pago.monto
        if obj_programa["cuotas"] == 16:
            pagos_total = (4 * obj_programa["costo"]) * pago_ciclo
        elif obj_programa["cuotas"] == 18:
            pagos_total = (6 * obj_programa["costo"]) * pago_ciclo
        elif obj_programa["cuotas"] == 24:
            pagos_total = (6 * obj_programa["costo"]) * pago_ciclo
        elif obj_programa["cuotas"] == 36:
            pagos_total = (6 * obj_programa["costo"]) * pago_ciclo

        if monto_total < (pagos_total - (4 * pago_ciclo)):
            mensaje = (
                "No puede realizar su matricula usted tiene una deuda de pension por un monto total de "
                + str(pagos_total - monto_total)
                + " Soles debe cancelar la deuda pendiente para poder continuar."
            )
            return Response({"mensaje": mensaje})
        # Tipo de programa
        obj_tipo_programa = Expediente.objects.filter(id=expediente_id).values(
            "programa__tipo_id"
        )
        tipo_programa = obj_tipo_programa[0]["programa__tipo_id"]
        if tipo_programa == 1:
            matriculas = (
                Matricula.objects.filter(
                    Q(promedio_final__isnull=True) | Q(promedio_final__gte=14) | Q(promedio_final_aplazado__gte=14),
                    expediente_id=expediente_id,
                )
                .exclude(is_retirado=True)
                .exclude()
                .values("curso_grupo__curso__id")
            )
        elif tipo_programa == 2:
            matriculas = (
                Matricula.objects.filter(
                    Q(promedio_final__isnull=True) | Q(promedio_final__gte=15) | Q(promedio_final_aplazado__gte=15),
                    expediente_id=expediente_id,
                )
                .exclude(is_retirado=True)
                .exclude()
                .values("curso_grupo__curso__id")
            )

        # ciclos ya matriculados
        obj_ciclo = (
            Matricula.objects.filter(expediente_id=expediente_id)
            .distinct("curso_grupo__curso__ciclo")
            .values("curso_grupo__curso__ciclo")
            .order_by("-curso_grupo__curso__ciclo")
            .first()
        )
        if obj_ciclo == None:
            ciclo = 1
        else:
            ciclo = obj_ciclo["curso_grupo__curso__ciclo"] + 1
        # cursos
        requisitos = (
            RequisitoCurso.objects.filter()
            .exclude(requisito_id__in=matriculas)
            .values("curso_id")
        )
        cursos = (
            Cursos.objects.filter(
                plan_estudio__programa_id=programa_id, ciclo__lte=ciclo
            )
            .exclude(id__in=matriculas)
            .exclude(id__in=requisitos)
            .order_by("ciclo", "id")
        )
        serializer = CursoMatriculaSerializer(cursos, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def get_cursos_grupos_by_cursos(request):
    if request.method == "GET":
        cursos = request.GET.get("cursos")
        cursos = cursos.split(",")
        if type(cursos) is list:
            cursos = list(cursos)
        else:
            return Response({"message": "cursos debe ser una lista"}, status=400)
        cursos_list_final = []
        DIAS = [
            "",
            "Lunes",
            "Martes",
            "Miercoles",
            "Jueves",
            "Viernes",
            "Sabado",
            "Domingo",
        ]

        for curso in cursos:
            curso_grupos = CursoGrupo.get_cursos_grupos_by_curso(
                curso, Periodo.get_periodo_activo().id
            ).order_by("id")
            if len(curso_grupos) > 0:
                obj_curso = {
                    "curso_id": curso,
                    "curso_nombre": curso_grupos[0].curso.nombre,
                }
                grupos = []
                for grupo in curso_grupos:
                    docente = (
                        grupo.docente.full_name() if grupo.docente else "no asignado"
                    )
                    limite_registros = grupo.limite_registros
                    numero_registros = (
                        Matricula.get_numero_registros_by_curso_grupo_periodo(
                            grupo.id, Periodo.get_periodo_activo().id
                        )
                    )
                    obj_grupo = {
                        "id": grupo.id,
                        "grupo": grupo.grupo,
                        "docente": docente,
                        "checked": False,
                        "limite_registros": limite_registros,
                        "numero_registros": numero_registros,
                        "horarios": [],
                    }

                    horarios = Horario.get_horarios_by_curso_grupo(grupo.id)
                    for horario in horarios:
                        obj_horario = {
                            "dia": DIAS[horario.dia],
                            "hora_inicio": horario.hora_inicio.strftime("%H:%M %p"),
                            "hora_fin": horario.hora_fin.strftime("%H:%M %p"),
                        }
                        obj_grupo["horarios"].append(obj_horario)
                    grupos.append(obj_grupo)
                cursos_list_final.append({**obj_curso, "grupos": grupos})
        return Response(cursos_list_final)


@api_view(["GET"])
def get_matricula_by_expediente_active(request):
    if request.method == "GET":
        expediente_id = request.GET.get("expediente")
        periodo = Periodo.get_periodo_activo()
        matricula = Matricula.get_matricula_by_expediente_periodo(
            expediente_id, periodo.id
        )
        serializer = MatriculaSerializer(matricula, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def get_horarios_matriculados_by_expediente(request):
    if request.method == "GET":
        expediente_id = request.GET.get("expediente")
        periodo = Periodo.get_periodo_activo()
        cursos_matriculados = Matricula.get_matricula_by_expediente_periodo(
            expediente_id, periodo.id
        )

        data_final = []
        DIAS = [
            "",
            "Lunes",
            "Martes",
            "Miercoles",
            "Jueves",
            "Viernes",
            "Sabado",
            "Domingo",
        ]

        for matricula in cursos_matriculados:
            curso_grupo = CursoGrupo.objects.get(id=matricula.curso_grupo.id)
            obj_curso = {
                "curso_id": curso_grupo.curso.id,
                "curso_nombre": curso_grupo.curso.nombre,
            }
            grupos = []
            docente = (
                curso_grupo.docente.full_name()
                if curso_grupo.docente
                else "no asignado"
            )
            obj_grupo = {
                "id": curso_grupo.id,
                "grupo": curso_grupo.grupo,
                "docente": docente,
                "checked": True,
                "limite_registros": 0,
                "numero_registros": 0,
                "horarios": [],
            }

            horarios = Horario.get_horarios_by_curso_grupo(curso_grupo.id)
            for horario in horarios:
                obj_horario = {
                    "dia": DIAS[horario.dia],
                    "hora_inicio": horario.hora_inicio.strftime("%H:%M %p"),
                    "hora_fin": horario.hora_fin.strftime("%H:%M %p"),
                }
                obj_grupo["horarios"].append(obj_horario)

            grupos.append(obj_grupo)
            data_final.append({**obj_curso, "grupos": grupos})
        return Response(data=data_final)


@api_view(["GET"])
def get_cursos_matriculados_by_expediente(request):
    if request.method == "GET":
        expediente_id = request.GET.get("expediente_id")
        periodo_id = request.GET.get("periodo_id")
        cursos_matriculados = Matricula.get_matricula_by_expediente_periodo(
            expediente_id, periodo_id
        ).order_by("curso_grupo__curso__codigo")

        data_final = []

        for matricula in cursos_matriculados:
            if matricula.is_publicado:
                if matricula.is_aplazado:
                    if matricula.promedio_final_aplazado == None:
                        promedio_final = ""
                    else:
                        promedio_final = "{:.2f}".format(
                            matricula.promedio_final_aplazado
                        )
                else:
                    # promedio final tiene dos digitos decimales Y TRASNFORMARLO EN ESTE FORMATO 12.00
                    promedio_final = "{:.2f}".format(matricula.promedio_final)

            else:
                promedio_final = ""
            curso_grupo = CursoGrupo.objects.get(id=matricula.curso_grupo.id)
            obj_curso = {
                "curso_id": curso_grupo.curso.id,
                "curso_nombre": curso_grupo.curso.nombre,
            }
            grupo = curso_grupo.grupo
            data_final.append(
                {**obj_curso, "grupo": grupo, "promedio_final": promedio_final}
            )
        return Response(data=data_final)


@api_view(["GET"])
def get_cursos_by_docente(request):
    if request.method == "GET":
        persona_id = request.GET.get("persona_id")
        periodo_id = request.GET.get("periodo_id")
        cursos = CursoGrupo.get_cursos_by_docente(persona_id, periodo_id)
        serializer = CursoGrupoSerializer(cursos, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def get_docente(request):
    if request.method == "GET":
        persona_id = request.GET.get("persona_id")
        docente = Persona.get_docente_by_id_persona(persona_id)
        serializer = ExpedienteDocenteserializer(docente, many=False)
        return Response(serializer.data)


@api_view(["GET"])
def get_alumnos_curso_grupo_by_id(request):
    if request.method == "GET":
        curso_grupo_id = request.GET.get("curso_grupo_id")
        matriculas = Matricula.get_curso_grupo_by_id(curso_grupo_id)
        expedientes = []
        for matricula in matriculas:
            obj_expediente = {
                "expediente_id": matricula.expediente.id,
                "promedio_final": matricula.promedio_final,
            }

            expedientes.append(obj_expediente)
        alumnos = []
        for expediente in expedientes:
            alumno = Expediente.get_alumno_by_expediente_id(expediente["expediente_id"])
            promedio_final = expediente["promedio_final"]
            serializer = ExpedienteAlumnoSerializer(alumno)
            alumnos.append({**serializer.data, "promedio_final": promedio_final})
        return Response(alumnos)


@api_view(["POST"])
def publicar_notas(request):
    if request.method == "POST":
        data = request.data
        periodo_id = data.get("periodo_id")
        curso_grupo_id = data.get("curso_grupo_id")
        matricula_obj = Matricula.objects.filter(
            periodo_id=periodo_id, curso_grupo_id=curso_grupo_id
        )
        for matricula in matricula_obj:
            matricula.is_publicado = True
            matricula.save()
        return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def cerrar_acta(request):
    if request.method == "POST":
        data = request.data
        periodo_id = data.get("periodo_id")
        curso_grupo_id = data.get("curso_grupo_id")
        from datetime import datetime

        date_now = datetime.now()
        matricula_obj = Matricula.objects.filter(
            periodo_id=periodo_id, curso_grupo_id=curso_grupo_id
        )
        for matricula in matricula_obj:
            matricula.fecha_cierre_acta = date_now.strftime("%Y-%m-%d")
            matricula.is_cerrado = True
            matricula.save()
        return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
def get_estado_notas_curso_by_id(request):
    if request.method == "GET":
        curso_grupo_id = request.GET.get("curso_grupo_id")
        periodo_id = request.GET.get("periodo_id")
        matricula_obj = Matricula.objects.filter(
            periodo_id=periodo_id, curso_grupo_id=curso_grupo_id
        ).first()
        if matricula_obj:
            return Response(
                {
                    "is_cerrado": matricula_obj.is_cerrado,
                    "is_publicado": matricula_obj.is_publicado,
                }
            )

        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["PUT"])
def save_notas(request):
    if request.method == "PUT":
        data = request.data
        periodo_id = data.get("periodo_id")
        curso_grupo_id = data.get("curso_grupo_id")
        alumnos = data.get("alumnos")
        for alumno in alumnos:
            if alumno["promedio_final"] is not None:
                if (
                    float(alumno["promedio_final"]) >= 0.0
                    and float(alumno["promedio_final"]) <= 20.0
                ):
                    matricula_obj = Matricula.objects.filter(
                        periodo_id=periodo_id,
                        curso_grupo_id=curso_grupo_id,
                        expediente_id=alumno["id"],
                    )
                    for matricula in matricula_obj:
                        matricula.promedio_final = float(alumno["promedio_final"])
                        matricula.save()
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
def get_persona(request):
    if request.method == "GET":
        numero_documento = request.GET.get("numero_documento")
        personas = Expediente.get_expediente_by_numero_documento(numero_documento)
        if not personas:
            return Response({"message": "Persona no encontrado"}, status=404)
        programas = []
        for persona in personas:
            programa = Programa.get_programa_by_id(persona.programa_id)
            obj_programa = ProgramaSerializer(programa)
            programas.append({**obj_programa.data, "expediente_id": persona.id})

        serializer = ExpedientePersonaSerializer(persona)

        return Response({**serializer.data, "programas": programas})


@api_view(["GET"])
def get_matriculas(request):
    if request.method == "GET":
        periodo = request.GET.get("periodo_id")
        search = request.GET.get("search")
        programa = request.GET.get("programa_id")
        if programa == "0":
            print(programa)
            matriculas = (
                Matricula.objects.all()
                .filter(
                    Q(expediente__persona__numero_documento__icontains=search)
                    | Q(expediente__persona__apellido_paterno__icontains=search)
                    | Q(expediente__persona__apellido_materno__icontains=search),
                    periodo__id=periodo,
                )
                .distinct("expediente_id", "periodo__id")
                .order_by("-expediente_id")[:25]
            )

        else:
            matriculas = (
                Matricula.objects.all()
                .filter(
                    Q(expediente__persona__numero_documento__icontains=search)
                    | Q(expediente__persona__apellido_paterno__icontains=search)
                    | Q(expediente__persona__apellido_materno__icontains=search),
                    periodo__id=periodo,
                    expediente__programa__id=programa,
                )
                .distinct("expediente_id", "periodo__id")
                .order_by("-expediente_id")[:25]
            )

        expedientes = []
        for matricula in matriculas:
            obj_expediente = {
                "expediente_id": matricula.expediente.id,
                "periodo": matricula.periodo.nombre,
                "fecha": matricula.fecha,
            }

            expedientes.append(obj_expediente)
        alumnos = []
        for expediente in expedientes:
            alumno = Expediente.get_alumno_by_expediente_id(expediente["expediente_id"])
            periodo = expediente["periodo"]
            fecha = expediente["fecha"]
            serializer = ExpedienteMatriculaSerializer(alumno)
            alumnos.append({**serializer.data, "periodo": periodo, "fecha": fecha})
        return Response(alumnos)


@api_view(["GET"])
def get_expedientes(request):
    if request.method == "GET":
        search = request.GET.get("search")
        programa = request.GET.get("programa_id")
        promocion = request.GET.get("promocion")
        if programa == "0":
            data = Expediente.objects.filter(
                Q(persona__numero_documento__icontains=search)
                | Q(persona__apellido_paterno__icontains=search)
                | Q(persona__apellido_materno__icontains=search),
                promocion__icontains=promocion,
            ).order_by("-id")[:25]
        else:
            data = Expediente.objects.filter(
                Q(persona__numero_documento__icontains=search)
                | Q(persona__apellido_paterno__icontains=search)
                | Q(persona__apellido_materno__icontains=search),
                promocion__icontains=promocion,
                programa__id=programa,
            ).order_by("-id")[:25]
        expedientes = []
        for expediente in data:
            serializer = ExpedienteMatriculaSerializer(expediente)
            expedientes.append({**serializer.data})

        return Response(expedientes)


@api_view(["GET"])
def get_programas_by_periodo(request):
    if request.method == "GET":
        periodo = request.GET.get("periodo_id")
        data = (
            CursoGrupo.objects.all()
            .filter(periodo__id=periodo)
            .distinct("curso__plan_estudio__programa__id")
        )
        Programas = []
        for Programa in data:
            obj_Programas = {
                "id": Programa.curso.plan_estudio.programa.id,
                "codigo": Programa.curso.plan_estudio.programa.codigo,
                "nombre": Programa.curso.plan_estudio.programa.nombre,
            }

            Programas.append(obj_Programas)
    return Response(Programas)


@api_view(["GET"])
def get_alumno_by_expediente(request):
    if request.method == "GET":
        expediente = request.GET.get("expediente_id")
        alumno = Expediente.get_alumno_by_expediente_id(expediente)
        if not alumno:
            return Response({"message": "Alumno no encontrado"}, status=404)
        serializer = ExpedienteAlumnoSerializer(alumno)
        return Response(serializer.data)


@api_view(["GET"])
def get_alumno_by_dni(request):
    if request.method == "GET":
        dni = request.GET.get("dni")
        alumno = Expediente.objects.filter(
            persona__numero_documento=dni, is_active=True
        ).first()
        if not alumno:
            return Response({"message": "Alumno no encontrado"}, status=404)
        serializer = ExpedienteAlumnoSerializer(alumno)
        return Response(serializer.data)


@api_view(["GET"])
def get_progreso_academico_by_expediente_id(request):
    if request.method == "GET":
        expediente_id = request.GET.get("expediente_id")
        cursos = (
            Matricula.get_progreso_academico_by_expediente(expediente_id)
            .exclude(is_retirado=True)
            .order_by("periodo","curso_grupo__curso__codigo")
        )
        data = []

        for matricula in cursos:
            if matricula.is_aplazado == True:
                if matricula.promedio_final_aplazado == None:
                    promedio_final = ""
                else:
                    promedio_final = "{:.2f}".format(matricula.promedio_final_aplazado)
            else:
                promedio_final = "{:.2f}".format(matricula.promedio_final)

            curso_grupo = CursoGrupo.objects.get(id=matricula.curso_grupo.id)
            obj_curso = {
                "id": curso_grupo.curso.id,
                "codigo": curso_grupo.curso.codigo,
                "nombre": curso_grupo.curso.nombre,
                "creditos": curso_grupo.curso.creditos,
                "periodo": curso_grupo.periodo.nombre,
                "grupo": curso_grupo.grupo,
                "docente": curso_grupo.docente.persona.get_full_name(),
                "fecha_inicio": curso_grupo.fecha_inicio,
                "fecha_termino": curso_grupo.fecha_termino,
                "fecha_cierre_acta": matricula.fecha_cierre_acta,
            }
            data.append({**obj_curso, "promedio_final": promedio_final})
        return Response(data)


@api_view(["POST"])
def get_periodos_by_expediente_id(request):
    expediente_id = request.data.get("expediente_id")
    periodos = (
        Matricula.objects.filter(expediente__id=expediente_id)
        .values(
            "periodo__id",
            "periodo__nombre",
            "periodo__fecha_inicio",
            "periodo__fecha_fin",
            "periodo__is_active",
            "periodo__is_active_matricula",
        )
        .distinct()
    )
    obj_periodos = []
    for periodo in periodos:
        obj_periodo = {
            "id": periodo["periodo__id"],
            "nombre": periodo["periodo__nombre"],
            "fecha_inicio": periodo["periodo__fecha_inicio"],
            "fecha_fin": periodo["periodo__fecha_fin"],
            "is_active": periodo["periodo__is_active"],
            "is_active_matricula": periodo["periodo__is_active_matricula"],
        }
        obj_periodos.append(obj_periodo)
    return Response(obj_periodos)
