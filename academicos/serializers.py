from rest_framework.serializers import ModelSerializer

from academicos.models import *

class ProgramaSerializer(ModelSerializer):
    class Meta:
        model = Programa
        fields = "__all__"

class FacultadSerializer(ModelSerializer):
    class Meta:
        model = Facultad
        fields = "__all__"


# cursos, docente, horario, matricula
class CursosSerializer(ModelSerializer):
    class Meta:
        model = Cursos
        fields = "__all__"


class DocenteSerializer(ModelSerializer):
    class Meta:
        model = Docente
        fields = "__all__"


class HorarioSerializer(ModelSerializer):
    class Meta:
        model = Horario
        fields = "__all__"


class MatriculaSerializer(ModelSerializer):
    class Meta:
        model = Matricula
        fields = "__all__"


from rest_framework import serializers
class CursoMatriculaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    ciclo = serializers.CharField()
    creditos = serializers.IntegerField()
    codigo = serializers.CharField()


class HoarioMatriculaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    dia = serializers.SerializerMethodField(source="get_dia")
    hora_inicio = serializers.SerializerMethodField(source="get_hora_inicio")
    hora_fin = serializers.SerializerMethodField(source="get_hora_fin")
    curso_id = serializers.IntegerField(source="curso_grupo.curso.id")

    def get_hora_inicio(self, obj):
        return obj.hora_inicio.strftime("%H:%M %p")

    def get_hora_fin(self, obj):
        return obj.hora_fin.strftime("%H:%M %p")

    def get_dia(self, obj): 
        DIAS = (
            (1, "Lunes"),
            (2, "Martes"),
            (3, "Miercoles"),
            (4, "Jueves"),
            (5, "Viernes"),
            (6, "Sabado"),
            (7, "Domingo"),
        )
        return DIAS[obj.dia - 1][1]         


class CursoGrupoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    docente_nombre = serializers.SerializerMethodField(source="get_docente_nombre")
    curso_id = serializers.IntegerField(source="curso.id")
    curso_nombre = serializers.CharField(source="curso.nombre")
    programa_nombre = serializers.SerializerMethodField(source="get_programa_nombre") 
    grupo = serializers.CharField()     
    horarios = serializers.SerializerMethodField(source="get_horarios")     

    def get_docente_nombre(self, obj):
        if not obj.docente:
            return ""
        return obj.docente.full_name()
    
    def get_horarios(self, obj):
        return HoarioMatriculaSerializer(obj.horario_set.all(), many=True).data

    def get_programa_nombre(self, obj):
        if not obj.curso.plan_estudio.programa:
            return "EXTRACURRICULAR"
        return obj.curso.plan_estudio.programa.nombre    

class ExpedienteDocenteserializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombres = serializers.CharField()
    apellido_paterno = serializers.CharField()
    apellido_materno = serializers.CharField()
    numero_documento = serializers.CharField()
    foto = serializers.SerializerMethodField(source="get_foto")
    correo = serializers.CharField()      
    celular = serializers.CharField()

    def get_foto(self, obj):
        return ""
        if not obj.foto:
            return ""
        return obj.foto

from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin,
)


class MatriculaBulkSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = Matricula
        fields = "__all__"
        list_serializer_class = BulkListSerializer


class MatriculaNotasSerializer(BulkListSerializer,ModelSerializer):
    expediente_id = serializers.IntegerField(source="expediente.id")
    curso_grupo_id = serializers.IntegerField(source="curso_grupo.id")
    peridodo_id = serializers.IntegerField(source="periodo.id")
    promedio_final = serializers.DecimalField( max_digits=2, decimal_places=2)
    list_serializer_class = BulkListSerializer