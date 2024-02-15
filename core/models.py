from typing import Iterable
from django.db import models

from zonas.models import Pais

from django.contrib.auth.models import User, Group


# Create your models here.


# crear una clase Abstracta para que se herede en los demas modelos
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)

    class Meta:
        abstract = True


class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Persona(BaseModel):
    tipo_documento = models.ForeignKey(
        TipoDocumento, on_delete=models.CASCADE, null=True, blank=True
    )
    numero_documento = models.CharField(
        max_length=20, null=True, blank=True, unique=True
    )
    nombres = models.CharField(max_length=50, null=True, blank=True)
    apellido_paterno = models.CharField(max_length=50, null=True, blank=True)
    apellido_materno = models.CharField(max_length=50, null=True, blank=True)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, null=True, blank=True)
    SEXOS = (
        ("M", "Masculino"),
        ("F", "Femenino"),
    )
    sexo = models.CharField(max_length=1, choices=SEXOS, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    correo = models.EmailField(max_length=254, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    user = models.OneToOneField(
        "auth.User", on_delete=models.CASCADE, null=True, blank=True
    )
    foto = models.ImageField(upload_to="fotos", null=True, blank=True)
    celular = models.CharField(max_length=20, null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)

    def get_full_name(self):
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}"

    def get_full_last_name(self):
        return f"{self.apellido_paterno} {self.apellido_materno}"

    def __str__(self):
        return f"{self.numero_documento} {self.nombres} {self.apellido_paterno} {self.apellido_materno} ({self.correo})"

    @staticmethod
    def get_docente_by_id_persona(persona_id):
        return Persona.objects.filter(id=persona_id).first()

    @staticmethod
    def get_persona_by_numero_id(numero_documento):
        return Persona.objects.filter(numero_documento=numero_documento)

    def save(self, *args, **kwargs):
        if self.full_name is None or self.full_name == "":
            self.full_name = self.get_full_name()
        super(Persona, self).save(*args, **kwargs)


class Periodo(models.Model):
    nombre = models.CharField(max_length=50)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    is_active = models.BooleanField(default=True)
    is_active_matricula = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    @staticmethod
    def get_periodo_activo():
        periodo = Periodo.objects.filter(is_active=True).first()
        return periodo

    @staticmethod
    def get_periodo_by_etapa_active(programa_id, promocion, is_academico):
        if is_academico:
            etapa = Etapa.objects.filter(
                programa__id=programa_id, promocion=promocion, is_active=True
            ).first()
            if etapa is None:
                return None
            return etapa.periodo
        else:
            etapa = Etapa.objects.filter(
                programa__id=programa_id, promocion=promocion, is_active_matricula=True
            ).first()
            return etapa.periodo

    @staticmethod
    def get_periodos():
        periodos = Periodo.objects.all()
        return periodos


class Etapa(models.Model):
    descipcion = models.CharField(max_length=250)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    programa = models.ForeignKey("academicos.Programa", on_delete=models.CASCADE)
    promocion = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_active_matricula = models.BooleanField(default=True)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    fecha_extemporaneo_inicio = models.DateField(blank=True, null=True)
    fecha_extemporaneo_fin = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.descipcion} - Programa: {self.programa.nombre} - Periodo:{self.periodo.nombre}"

    @staticmethod
    def get_etapa_activo(programa_id, promocion):
        return Etapa.objects.filter(
            programa_id=programa_id, promocion=promocion, is_active=True
        ).first()


class Area(models.Model):
    nombre = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    key_name = models.CharField(max_length=100, null=True, blank=True)
    charge_number = models.IntegerField(default=0)
    is_external = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre}"


class Cargo(models.Model):
    nombre = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.is_active}"


class Headquarter(models.Model):
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "headquarter"
        verbose_name_plural = "headquarters"

    def __str__(self):
        return self.name


class CargoArea(models.Model):
    GRADOS = (
        ("Bach.", "Bachiller"),
        ("Lic.", "Licenciado"),
        ("Ing.", "Ingeniero"),
        ("Mtro.", "Maestro"),
        ("Dr.", "Doctorado"),
        ("C.P.C.", "Contador Público"),
    )

    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    grado_academico = models.CharField(
        max_length=50, null=True, blank=True, choices=GRADOS
    )
    area = models.ManyToManyField(Area)
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE)
    headquarter = models.ForeignKey(
        Headquarter, on_delete=models.CASCADE, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.persona.nombres} {self.persona.apellido_paterno} {self.persona.apellido_materno} - {self.cargo.nombre}"


class Apps(models.Model):
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=50)
    icon = models.CharField(max_length=50)
    background = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.url} - {self.is_active}"

    @staticmethod
    def get_apps():
        return Apps.objects.filter(is_active=True)


class Menu(models.Model):
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=50)
    icon = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    app = models.ForeignKey(Apps, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group)

    def __str__(self):
        return f"{self.name} - {self.url} - {self.is_active}"


class PersonaJuridica(BaseModel):
    tipo_documento = models.ForeignKey(
        TipoDocumento, on_delete=models.CASCADE, null=True, blank=True
    )
    numero_documento = models.CharField(
        max_length=20, null=True, blank=True, unique=True
    )
    razon_social = models.CharField(max_length=50)
    correo = models.EmailField(max_length=254, null=True, blank=True)
    celular = models.CharField(max_length=20, null=True, blank=True)
    persona_contacto = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.numero_documento} {self.razon_social} ({self.correo})"

    @staticmethod
    def get_persona_juridica_by_numero_id(numero_documento):
        return PersonaJuridica.objects.filter(numero_documento=numero_documento)

    @staticmethod
    def get_persona_juridica_by_razaon_social(razon_social):
        return PersonaJuridica.objects.filter(razon_social=razon_social)
