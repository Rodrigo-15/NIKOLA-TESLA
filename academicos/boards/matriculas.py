from django.contrib import admin


class MatriculaBoard(admin.ModelAdmin):
    list_display = ('id','expediente','curso_grupo','periodo','fecha',)  # Campos a mostrar en la lista
    search_fields = ('expediente__persona__numero_documento','curso_grupo__curso__nombre','periodo__nombre','fecha',)  # Campos de busqueda
    list_filter = ('periodo',)  # Filtros en la lista