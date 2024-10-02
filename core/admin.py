from django.contrib import admin
from core.models import *
from core.boards import *
# Register your models here.


admin.site.register(TipoDocumento)
admin.site.register(Persona, PersonaBoard)
admin.site.register(Periodo)
admin.site.register(Etapa, EtapaBoard)
admin.site.register(Area)
admin.site.register(Cargo)
admin.site.register(CargoArea)
admin.site.register(Apps)
admin.site.register(Menu)
admin.site.register(Headquarter)
admin.site.register(PersonaJuridica)