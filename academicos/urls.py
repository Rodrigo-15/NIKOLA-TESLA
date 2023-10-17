from django.urls import path, include
from .router import router, router_bulk
from .views import *

urlpatterns = [
    path("get_alumno", get_alumno, name="get_alumno"),
    path("get_persona", get_persona, name="get_persona"),
    path(
        "get_cursos_by_programa_id",
        get_cursos_by_programa_id,
        name="get_cursos_by_programa_id",
    ),
    path(
        "get_cursos_grupos_by_cursos",
        get_cursos_grupos_by_cursos,
        name="get_cursos_grupos_by_cursos",
    ),
    path("", include(router.urls)),
    path("bulks/", include(router_bulk.urls)),
    path(
        "get_matricula_by_expediente_active",
        get_matricula_by_expediente_active,
        name="get_matricula_by_expediente_active",
    ),
    path(
        "get_horarios_matriculados_by_expediente",
        get_horarios_matriculados_by_expediente,
        name="get_horarios_matriculados_by_expediente",
    ),
    path("get_cursos_by_docente", get_cursos_by_docente, name="get_cursos_by_docente"),
    path("get_docente", get_docente, name="get_docente"),
    path(
        "get_alumnos_curso_grupo_by_id",
        get_alumnos_curso_grupo_by_id,
        name="get_alumnos_curso_grupo_by_id",
    ),
    path("publicar_notas", publicar_notas, name="publicar_notas"),
    path("cerrar_acta", cerrar_acta, name="cerrar_acta"),
    path("save_notas", save_notas, name="save_notas"),
    path(
        "get_estado_notas_curso_by_id",
        get_estado_notas_curso_by_id,
        name="get_estado_notas_curso_by_id",
    ),
    path(
        "get_cursos_matriculados_by_expediente",
        get_cursos_matriculados_by_expediente,
        name="get_cursos_matriculados_by_expediente",
    ),
    path("get_matriculas", get_matriculas, name="get_matriculas"),
    path("get_expedientes", get_expedientes, name="get_expedientes"),
    path(
        "get_programas_by_periodo",
        get_programas_by_periodo,
        name="get_programas_by_periodo",
    ),
    path(
        "get_alumno_by_expediente",
        get_alumno_by_expediente,
        name="get_alumno_by_expediente",
    ),
    path("get_alumno_by_dni", get_alumno_by_dni, name="get_alumno_by_dni"),
    path(
        "get_progreso_academico_by_expediente_id",
        get_progreso_academico_by_expediente_id,
        name="get_progreso_academico_by_expediente_id",
    ),
    path(
        "get_periodos_by_expediente_id",
        get_periodos_by_expediente_id,
        name="get_periodos_by_expediente_id",
    ),
    path(
        "get_periodos_by_docente_id",
        get_periodos_by_docente_id,
        name="get_periodos_by_docente_id",
    ),
    path(
        "get_periodos_by_aplazado_by_docente_id",
        get_periodos_by_aplazado_by_docente_id,
        name="get_periodos_by_aplazado_by_docente_id",
    ),
    path(
        "get_cursos_aplazado_by_docente",
        get_cursos_aplazado_by_docente,
        name="get_cursos_aplazado_by_docente",
    ),
    path(
        "get_alumnos_aplazado_curso_grupo_by_id",
        get_alumnos_aplazado_curso_grupo_by_id,
        name="get_alumnos_aplazado_curso_grupo_by_id",
    ),
    path(
        "save_notas_aplazado",
        save_notas_aplazado,
        name="save_notas_aplazado",
    ),
    path(
        "get_estado_notas_curso_aplazado_by_id",
        get_estado_notas_curso_aplazado_by_id,
        name="get_estado_notas_curso_aplazado_by_id",
    ),
    path(
        "publicar_notas_aplazado",
        publicar_notas_aplazado,
        name="publicar_notas_aplazado",
    ),
    path(
        "cerrar_acta_aplazado",
        cerrar_acta_aplazado,
        name="cerrar_acta_aplazado",
    ),
    path(
        "get_alumno_identificacion",
        get_alumno_identificacion,
        name="get_alumno_identificacion",
    ),
    path(
        "horario_dia_curso_grupo",
        horario_dia_curso_grupo,
        name="horario_dia_curso_grupo",
    ),
]
