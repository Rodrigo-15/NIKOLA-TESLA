from django.db import models
from django.contrib.auth.models import User
from core.models import Persona, Area
from django.db.models import Q

# Create your models here.


class Sede(models.Model):
    nombre = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'sedes'

    @staticmethod
    def get_sede_by_nombre(nombre):
        return Sede.objects.filter(nombre=nombre)

    def __str__(self):
        return self.nombre


class Expediente(models.Model):
    asunto = models.TextField(default='')
    fecha_hora = models.DateTimeField(auto_now_add=True, auto_now=False)
    ultima_modificacion = models.DateTimeField(
        auto_now_add=False, auto_now=True)
    is_activo = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'expediente'
        verbose_name_plural = 'expedientes'

    @staticmethod
    def get_last_expediente_id():
        return Expediente.objects.filter().values('id').last()['id']


class RequisitoTramite(models.Model):
    descripcion = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'requisito de tramite'
        verbose_name_plural = 'requisitos de los tramites'

    @staticmethod
    def get_requisito_tramite(descripcion):
        return RequisitoTramite.objects.filter(descripcion=descripcion)

    def __str__(self):
        return self.descripcion


class TipoTramite(models.Model):
    descripcion = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'tipo de tramite'
        verbose_name_plural = 'tipos de tramites'

    @staticmethod
    def get_tipo_tramite_by_descripcion(descripcion):
        return TipoTramite.objects.filter(descripcion=descripcion)

    def __str__(self):
        return self.descripcion


class Tramite(models.Model):
    expediente = models.ForeignKey(Expediente, on_delete=models.CASCADE)
    persona = models.ForeignKey(
        Persona, on_delete=models.CASCADE, null=True, blank=True)
    persona_entidad = models.CharField(max_length=30, null=True, blank=True)
    num_documento = models.CharField(
        max_length=20, null=True, blank=True)
    tipo_tramite = models.ForeignKey(
        TipoTramite, on_delete=models.CASCADE, verbose_name='tipo de tramite')
    asunto = models.TextField(max_length=250, null=True)
    num_doc_referencia = models.TextField(max_length=250, null=True)  # futuro adjuntor de archivos
    # usuario quien registró el tramite
    usuario = models.OneToOneField(
        'auth.User', on_delete=models.CASCADE, blank=True, null=True)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'tramite'
        verbose_name_plural = 'tramites'

    @staticmethod
    def get_last_tramite_id():
        return Tramite.objects.filter().values('id').last()['id']

    @staticmethod
    def get_tramite_by_id(tramite_id):
        return Tramite.objects.filter(id=tramite_id)

    def __str__(self):
        return f'{self.tipo_tramite} - {self.asunto} - {self.sede} - {self.fecha_hora} - {self.updated_at}'


class Tramite_Requisito(models.Model):
    """Tabla intermedia entre Tramites y RequisitosTramites."""

    tipo_tramite = models.ForeignKey(
        TipoTramite, on_delete=models.CASCADE, verbose_name='tipo de tramite')
    requisito = models.ForeignKey(
        RequisitoTramite, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'tramite y requisito'
        verbose_name_plural = 'tramites y requisitos'

    def __str__(self):
        return str(self.tipo_tramite)


class SeguimientoTramite(models.Model):
    tramite = models.ForeignKey(Tramite, on_delete=models.CASCADE)
    area_derivacion = models.ForeignKey(
        Area, on_delete=models.CASCADE, blank=True, verbose_name="area de derivacion")
    fecha_hora = models.DateTimeField(auto_now_add=True, auto_now=False)
    accion = models.CharField(max_length=250 , default='')
    is_iniciado = models.BooleanField(default=False)
    is_revision = models.BooleanField(default=False)
    is_concluido = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'seguimiento de los tramites'

    @staticmethod
    def get_seguimiento_by_tramite_id(tramite_id):
        return SeguimientoTramite.objects.filter(tramite_id=tramite_id)

    @staticmethod
    def get_seguimiento_activo_by_tramite_id(tramite_id):
        return SeguimientoTramite.objects.filter(Q(tramite_id=tramite_id) & (Q(is_iniciado=True) | Q(is_revision=True)))

    @staticmethod
    def get_area_derivacion_by_tramite_id(tramite_id):
        area = SeguimientoTramite.objects.filter(tramite_id=tramite_id).values(
            'area_derivacion_id').last()['area_derivacion_id']

        return area

    def __str__(self):
        return f'{self.tramite_id} - {self.area_derivacion}'
