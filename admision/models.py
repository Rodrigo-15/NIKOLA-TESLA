from this import d
from django.db import models
from core.models import Periodo, Persona
from academicos.models import Programa

# Create your models here.


class Expediente(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    programa = models.ForeignKey(Programa, on_delete=models.CASCADE)
    promocion = models.CharField(max_length=100, null=True, blank=True)
    periodo = models.ForeignKey(
        Periodo, on_delete=models.CASCADE, null=True, blank=True
    )
    res_rect_ingreso = models.CharField(
        max_length=100, null=True, blank=True, default=""
    )
    res_dirc_ingreso = models.CharField(
        max_length=100, null=True, blank=True, default=""
    )
    res_dirc_reingreso = models.CharField(
        max_length=100, null=True, blank=True, default=""
    )
    is_active = models.BooleanField(default=True, null=True, blank=True)
    is_retired = models.BooleanField(default=False, null=True, blank=True)
    is_graduate = models.BooleanField(default=False, null=True, blank=True)
    res_dir_retiro = models.CharField(max_length=100, null=True, blank=True, default="")
    codigo_universitario = models.CharField(
        max_length=100, null=True, blank=True, default=""
    )
    codigo_diploma = models.CharField(max_length=100, null=True, blank=True, default="")
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    res_diploma = models.CharField(max_length=100, null=True, blank=True, default="")
    fecha_diploma = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.persona} {self.programa} {self.promocion}"

    def get_full_name(self):
        return f"{self.persona.nombres} {self.persona.apellido_paterno} {self.persona.apellido_materno}"

    @staticmethod
    def get_expediente_by_numero_documento(numero_documento):
        return Expediente.objects.filter(
            persona__numero_documento=numero_documento, is_active=True
        )

    @staticmethod
    def get_alumno_by_id_persona(id):
        return Expediente.objects.filter(persona__id=id).first()

    @staticmethod
    def get_alumno_by_expediente_id(expediente_id):
        return Expediente.objects.filter(id=expediente_id).first()

    @staticmethod
    def get_alumno_by_numero_documento(numero_documento):
        return Expediente.objects.filter(
            persona__numero_documento=numero_documento, is_active=True
        ).first()

    @staticmethod
    def get_alumno_expedientes_by_id_persona(id):
        return Expediente.objects.filter(persona__id=id).order_by("-id")

    @staticmethod
    def get_alumno_expedientes_by_numero_documento(numero_documento):
        return Expediente.objects.filter(
            persona__numero_documento=numero_documento, is_active=True
        ).order_by("-id")
