from rest_framework import serializers
from academicos.models import Matricula
from admision.models import Expediente
from django.conf import settings
import os


class ExpedienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expediente
        fields = "__all__"


class ExpedienteReportSerializer(serializers.Serializer):
    programa_nombre = serializers.CharField(source="programa.nombre")
    promocion = serializers.CharField()
    nombres_apellidos = serializers.SerializerMethodField(
        source="get_nombres_apellidos"
    )

    def get_nombres_apellidos(self, obj):
        return (
            obj.persona.nombres
            + " "
            + obj.persona.apellido_paterno
            + " "
            + obj.persona.apellido_materno
        )


class ExpedienteAlumnoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombres = serializers.CharField(source="persona.nombres")
    apellido_paterno = serializers.CharField(source="persona.apellido_paterno")
    apellido_materno = serializers.CharField(source="persona.apellido_materno")
    numero_documento = serializers.CharField(source="persona.numero_documento")
    programa_nombre = serializers.CharField(source="programa.nombre")
    programa_id = serializers.IntegerField(source="programa.id")
    promocion = serializers.CharField()
    foto = serializers.SerializerMethodField(source="get_foto")
    correo = serializers.CharField(source="persona.correo")
    celular = serializers.CharField(source="persona.celular")

    def get_foto(self, obj):
        return ""
        if not obj.persona.foto:
            return ""
        return obj.persona.foto

    def get_promedio_final(self, obj):
        return None


class ExpedientePersonaSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="persona.id")
    nombres = serializers.CharField(source="persona.nombres")
    apellido_paterno = serializers.CharField(source="persona.apellido_paterno")
    apellido_materno = serializers.CharField(source="persona.apellido_materno")
    numero_documento = serializers.CharField(source="persona.numero_documento")
    correo = serializers.CharField(source="persona.correo")
    celular = serializers.CharField(source="persona.celular")


class ExpedienteMatriculaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombres = serializers.CharField(source="persona.nombres")
    apellido_paterno = serializers.CharField(source="persona.apellido_paterno")
    apellido_materno = serializers.CharField(source="persona.apellido_materno")
    numero_documento = serializers.CharField(source="persona.numero_documento")
    programa_nombre = serializers.CharField(source="programa.nombre")
    promocion = serializers.CharField()
    is_retired = serializers.BooleanField()
    foto = serializers.SerializerMethodField(source="get_foto")

    def get_foto(self, obj):
        if not obj.persona.foto:
            return ""
        return obj.persona.foto


class ExpedientesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    programa_nombre = serializers.CharField(source="programa.nombre")
    programa_id = serializers.IntegerField(source="programa.id")
    promocion = serializers.CharField()
    codigo_universitario = serializers.CharField()
