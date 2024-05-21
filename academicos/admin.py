from django.contrib import admin
from academicos.models import *
from academicos.boards import *

# Register your models here.
admin.site.register(Facultad)
admin.site.register(TipoPrograma)
admin.site.register(Programa)
admin.site.register(PlanEstudio)
admin.site.register(Cursos)
admin.site.register(Docente)
admin.site.register(Matricula, MatriculaBoard)
admin.site.register(Horario)
admin.site.register(CursoGrupo, CursoGrupoBoard)
admin.site.register(RequisitoCurso)
admin.site.register(Aplazado)
admin.site.register(Aula)
admin.site.register(AsistenciaDocente)
