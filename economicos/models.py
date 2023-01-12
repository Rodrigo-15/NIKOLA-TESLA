import datetime
from django.db import models
from academicos.models import Programa
from admision.models import Expediente

class HistoryImporBatch(models.Model):
    nombrebatch=models.CharField(max_length=70)
    fecha=models.DateField()
    fechaingreso=models.DateField(('Date'),default=datetime.date.today)

class Concepto(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    programa = models.ForeignKey(
        Programa, on_delete=models.CASCADE, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.codigo}"

    @staticmethod
    def get_concepto_by_id(id):
        return Concepto.objects.filter(id=id).first()


class Pago(models.Model):
    nombre_cliente = models.CharField(max_length=50)
    numero_documento = models.CharField(max_length=50)
    numero_operacion = models.CharField(max_length=50)
    fecha_operacion = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    concepto = models.ForeignKey(Concepto, on_delete=models.CASCADE)
    expendiente = models.ForeignKey(
        Expediente, on_delete=models.CASCADE, null=True, blank=True)
    numero_conciliacion = models.CharField(
        max_length=50, null=True, blank=True)
    is_conciliado = models.BooleanField(default=False)
    is_validado = models.BooleanField(default=False)
    adjunto = models.FileField(upload_to='adjuntos', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            numero_operacion = self.numero_operacion
            numero_documento = self.numero_documento
            exist = Pago.objects.filter(
                numero_operacion=numero_operacion,numero_documento=numero_documento).exists()
            if exist:
                raise ValueError(
                    "Ya existe un pago con ese número de operación")

        super().save(*args, **kwargs)
    def __str__(self):
        alumno = ""
        if self.expendiente:
            alumno = f"{self.expendiente.persona.nombres} {self.expendiente.persona.apellido_paterno} {self.expendiente.persona.apellido_materno}"
        return f"{self.nombre_cliente} - {self.numero_operacion} - {self.concepto} - {self.monto} - ({alumno})"

    @staticmethod
    def get_pagos_by_expediente(expediente):
        return Pago.objects.filter(expendiente=expediente )

    @staticmethod
    def get_pagos_pensiones_by_expediente(expediente):
        return Pago.objects.filter(expendiente=expediente, concepto__codigo__contains='PENSION')

    @staticmethod
    def get_pagos_by_anio(anio):
        return Pago.objects.filter(fecha_operacion__year=anio)
    
    @staticmethod
    def get_pagos_by_anio_and_mes(anio, mes):
        return Pago.objects.filter(fecha_operacion__year=anio, fecha_operacion__month=mes)
    
    @staticmethod
    def get_pagos_by_anio_and_mes_and_dia(anio, mes,dia):
        return Pago.objects.filter(fecha_operacion__year=anio, fecha_operacion__month=mes,fecha_operacion__day=dia)
    
    @staticmethod
    def get_pagos_sin_conciliar():
        return Pago.objects.filter(is_conciliado=False)        
         
    @staticmethod
    def get_pagos_del_dia(dia):
        return Pago.objects.filter(fecha_operacion__day=dia).order_by('-is_conciliado')