from django.contrib import admin

class PersonaBoard(admin.ModelAdmin):
    list_display = ('numero_documento','full_name','is_active')  # Campos a mostrar en la lista
    search_fields = ('numero_documento','full_name',)
    list_filter = ('is_active',)  # Filtros en la lista