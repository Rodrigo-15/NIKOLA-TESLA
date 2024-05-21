from django.contrib import admin


class PagoBoard(admin.ModelAdmin):
    list_display = ('id','numero_documento','nombre_cliente','numero_operacion','fecha_operacion','monto','concepto','is_active')  # Campos a mostrar en la lista
    search_fields = ('numero_documento','nombre_cliente','numero_operacion','concepto__nombre',)
    list_filter = ('is_active',)  # Filtros en la lista