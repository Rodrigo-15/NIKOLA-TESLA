from django.db import models

from zonas.models import Pais

from django.contrib.auth.models import User, Group


# Create your models here.


class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Persona(models.Model):
    tipo_documento = models.ForeignKey(
        TipoDocumento, on_delete=models.CASCADE, null=True, blank=True
    )
    numero_documento = models.CharField(max_length=20, null=True, blank=True)
    nombres = models.CharField(max_length=50, null=True, blank=True)
    apellido_paterno = models.CharField(max_length=50, null=True, blank=True)
    apellido_materno = models.CharField(max_length=50, null=True, blank=True)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, null=True, blank=True)
    SEXOS = (
        ("M", "Masculino"),
        ("F", "Femenino"),
    )
    sexo = models.CharField(max_length=1, choices=SEXOS)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    correo = models.EmailField(max_length=254, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    user = models.OneToOneField(
        "auth.User", on_delete=models.CASCADE, null=True, blank=True
    )
    foto = models.ImageField(upload_to="fotos", null=True, blank=True)
    celular = models.CharField(max_length=20, null=True, blank=True)

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
    def get_periodos():
        periodos = Periodo.objects.all()
        return periodos


class Etapa(models.Model):
    descipcion = models.CharField(max_length=250)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    programa = models.ForeignKey("academicos.Programa", on_delete=models.CASCADE)
    promocion = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    fecha_inicio = models.DateField( blank=True, null=True)
    fecha_fin = models.DateField( blank=True, null=True)
    fecha_extemporaneo_inicio = models.DateField( blank=True, null=True)
    fecha_extemporaneo_fin = models.DateField( blank=True, null=True)
    
    def __str__(self):
        return f"{self.descipcion} - Programa: {self.programa.nombre} - Periodo:{self.periodo.nombre}"

    @staticmethod
    def get_etapa_activo(programa_id, periodo_id, promocion):
        return Etapa.objects.filter(
            programa_id=programa_id, periodo_id=periodo_id, promocion=promocion
        ).first()


class Area(models.Model):
    nombre = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    key_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre}"


class Cargo(models.Model):
    nombre = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.is_active}"


class CargoArea(models.Model):
    
    from desk.models import Headquarter
    
    GRADOS = (
        ("Bach.", "Bachiller"),
        ("Lic.", "Licenciado"),
        ("Ing.", "Ingeniero"),
        ("Mtro.", "Maestro"),
        ("Dr.", "Doctorado"),
    )

    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    grado_academico = models.CharField(
        max_length=50, null=True, blank=True, choices=GRADOS
    )
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE)
    headquarter = models.ForeignKey(
        Headquarter, on_delete=models.CASCADE, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.persona.nombres} {self.persona.apellido_paterno} {self.persona.apellido_materno} - {self.area.nombre} - {self.cargo.nombre}"


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
