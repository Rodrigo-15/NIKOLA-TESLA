from django.contrib import admin


class CursoGrupoBoard(admin.ModelAdmin):
    list_display = ('id','grupo','curso','docente','periodo','fecha_inicio','fecha_termino','resolucion')  # Campos a mostrar en la lista
    search_fields = ('grupo','curso__nombre','curso__codigo','periodo__nombre','fecha_inicio','fecha_termino','resolucion',)
    list_filter = ('is_active',)  # Filtros en la lista