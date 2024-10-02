from django.contrib import admin

class EtapaBoard(admin.ModelAdmin):
    list_display = ('id','descipcion','programa','promocion','is_active','is_active_matricula')  # Campos a mostrar en la lista
    search_fields = ('id','descipcion','programa__nombre','promocion')
    list_filter = ('is_active','promocion','programa__nombre',)  # Filtros en la lista