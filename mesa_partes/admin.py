from django.contrib import admin

from .models import Sede, RequisitoTramite, TipoTramite, Tramite, Tramite_Requisito, SeguimientoTramite, Expediente

# Register your models here.
admin.site.register(Sede)
admin.site.register(RequisitoTramite)
admin.site.register(TipoTramite)
admin.site.register(Tramite)
admin.site.register(Tramite_Requisito)
admin.site.register(SeguimientoTramite)
admin.site.register(Expediente)
