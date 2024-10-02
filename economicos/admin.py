from django.contrib import admin
from .models import Concepto, Pago
from .boards import *

# Register your models here.
admin.site.register(Concepto)
admin.site.register(Pago, PagoBoard)