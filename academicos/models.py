
from django.db import models

from core.models import Periodo

# Create your models here.


class Facultad(models.Model):
    nombre = models.CharField(max_length=50)
    sigla = models.CharField(max_length=10)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        self.sigla = self.sigla.upper()
        super(Facultad, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} - {self.sigla}"


class TipoPrograma(models.Model):
    nombre = models.CharField(max_length=50)
    cantidad_matriculas = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(TipoPrograma, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} - {self.cantidad_matriculas}"


class Programa(models.Model):
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=250)
    is_active = models.BooleanField(default=True)
    tipo = models.ForeignKey(TipoPrograma, on_delete=models.CASCADE)
    facultad = models.ForeignKey(Facultad, on_delete=models.CASCADE)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    cuotas = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.id}. {self.nombre} - {self.codigo}"

    @staticmethod
    def get_programa_by_id(programa_id):
        return Programa.objects.filter(id=programa_id).first()

    


class PlanEstudio(models.Model):
    programa = models.ForeignKey(Programa, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=250)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id} - {self.nombre} - {self.programa.nombre}"


class Cursos(models.Model):
    plan_estudio = models.ForeignKey(PlanEstudio, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=250)
    ciclo = models.IntegerField(default=1)
    creditos = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    codigo = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"{self.id}. {self.nombre} - {self.ciclo} - {self.creditos} - {self.codigo}"
    
    @staticmethod
    def get_cursos_by_programa_id(programa_id):
        return Cursos.objects.filter(plan_estudio__programa_id=programa_id)
    
class RequisitoCurso(models.Model):
      curso = models.ForeignKey(Cursos,null=False, on_delete=models.CASCADE,related_name='curso_set')
      requisito = models.ForeignKey(Cursos,null=False, on_delete=models.CASCADE,related_name='requisito_set')
      def __str__(self):
        return f"{self.curso.codigo}-{self.curso.nombre}|{self.requisito.codigo}-{self.requisito.nombre}"

class Docente(models.Model):
    GRADOS = (
        ("M", "Magister"),
        ("D", "Doctorado"),
        ("P", "Postdoctorado"),
    )

    persona = models.OneToOneField('core.Persona', on_delete=models.CASCADE)
    grado_academico = models.CharField(max_length=50, choices=GRADOS)
    is_active = models.BooleanField(default=True)
     
    def full_name(self):
        if not self.persona:
            return ""
        return f"{self.persona.nombres} {self.persona.apellido_paterno} {self.persona.apellido_materno}"

    def __str__(self):
        return f"{self.full_name()} - {self.grado_academico}"
       

class CursoGrupo(models.Model):
    GRUPOS = (
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
        ("E", "E"),
        ("F", "F"),
        ("G", "G"),
        ("H", "H"),

    )
    periodo = models.ForeignKey('core.Periodo', on_delete=models.CASCADE)
    curso = models.ForeignKey(Cursos, on_delete=models.CASCADE)
    grupo = models.CharField(max_length=50, choices=GRUPOS)
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE, null=True, blank=True)
    limite_registros = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_termino = models.DateField(null=True, blank=True)
    resolucion = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        docente = self.docente.full_name() if self.docente else 'No asignado'
        return f"{self.id} - {self.curso.nombre} - {self.grupo} - {docente} (Programa: {self.curso.plan_estudio.programa.nombre})"
    
    @staticmethod
    def get_cursos_grupos_by_curso(curso_id,periodo_id):
        return CursoGrupo.objects.filter(curso__id=curso_id, periodo__id=periodo_id)
    
    @staticmethod
    def get_cursos_grupos_by_cursos(cursos_ids):
        return CursoGrupo.objects.filter(curso_id__in=cursos_ids).order_by("grupo")
    
    @staticmethod
    def get_cursos_by_docente(persona_id, periodo_id):
        return CursoGrupo.objects.filter(docente__persona_id=persona_id, periodo_id=periodo_id).order_by("grupo")
    

class Horario(models.Model):
    DIAS = (
        (1, "Lunes"),
        (2, "Martes"),
        (3, "Miercoles"),
        (4, "Jueves"),
        (5, "Viernes"),
        (6, "Sabado"),
        (7, "Domingo"),
    )     
    curso_grupo = models.ForeignKey(CursoGrupo, on_delete=models.CASCADE, null=True, blank=True)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    dia = models.IntegerField(choices=DIAS)     
    is_active = models.BooleanField(default=True)
    
    def get_dia(self):
        return self.DIAS[self.dia - 1][1]     

    def get_full_horario(self):
        return f"{self.get_dia()} - {self.hora_inicio} - {self.hora_fin}"

    @staticmethod
    def get_horarios_by_curso_grupo(curso_grupo_id):
        return Horario.objects.filter(curso_grupo__id=curso_grupo_id)


    def __str__(self):         
        curso_nombre = self.curso_grupo.curso.nombre if self.curso_grupo else 'No asignado'
        grupo_nombre = self.curso_grupo.grupo if self.curso_grupo else 'No asignado'
        return f"{self.get_full_horario()} - {curso_nombre} - {grupo_nombre}"


class Matricula(models.Model):
    expediente = models.ForeignKey(
        "admision.Expediente", on_delete=models.CASCADE)
    curso_grupo = models.ForeignKey(CursoGrupo, on_delete=models.CASCADE, null=True, blank=True)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    promedio_final = models.DecimalField(max_digits=4,decimal_places=2,null=True, blank=True)
    is_publicado = models.BooleanField(default=False)
    is_cerrado = models.BooleanField(default=False)  
    is_retirado = models.BooleanField(default=False)  
    fecha = models.DateField(auto_now_add=True,null=True, blank=True)
    fecha_cierre_acta = models.DateField(auto_now=False,auto_now_add=False,null=True, blank=True)
    fecha_modified = models.DateTimeField(auto_now=True,null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.periodo = Periodo.get_periodo_activo()

        super(Matricula, self).save(*args, **kwargs)

    def __str__(self):
        curso_nombre = self.curso_grupo.curso.nombre if self.curso_grupo else 'No asignado'
        grupo_nombre = self.curso_grupo.grupo if self.curso_grupo else 'No asignado'
        return f"{self.id} - Grupo: {grupo_nombre} - Curso: {curso_nombre} ({self.periodo.nombre}) {self.expediente.id}"

    @staticmethod
    def get_numero_registros_by_curso_grupo_periodo(curso_grupo_id, periodo_id):
        return Matricula.objects.filter(curso_grupo__id=curso_grupo_id, periodo__id=periodo_id).count()
    
    @staticmethod
    def get_matricula_by_expediente_periodo(expediente_id, periodo_id):
        return Matricula.objects.filter(expediente__id=expediente_id, periodo__id=periodo_id,is_retirado=False)
    
    @staticmethod
    def get_curso_grupo_by_id(curso_grupo_id):
        return Matricula.objects.filter(curso_grupo__id =curso_grupo_id, expediente__is_active=True, is_retirado = False).order_by('expediente__persona__apellido_paterno', 'expediente__persona__apellido_materno')
    
    @staticmethod
    def get_progreso_academico_by_expediente(expediente_id):
        return Matricula.objects.filter(expediente__id=expediente_id,is_retirado=False,is_cerrado=True)


