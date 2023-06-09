from rest_framework import serializers
from core.models import *


class PeriodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periodo
        fields = "__all__"


class EtapaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etapa
        fields = "__all__"


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = "__all__"


class MenuSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=200)
    url = serializers.CharField(max_length=200)
    icon = serializers.CharField(max_length=200)
    app = serializers.SerializerMethodField(source="get_app")

    def get_app(self, obj):
        return obj.app.name


class PersonSerializer(serializers.ModelSerializer):
    fecha_nacimiento = serializers.DateField(format="%Y/%m/%d")

    class Meta:
        model = Persona
        fields = "__all__"


class PersonListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    nombres = serializers.CharField(max_length=200)
    apellido_paterno = serializers.CharField(max_length=200)
    apellido_materno = serializers.CharField(max_length=200)
    numero_documento = serializers.CharField(max_length=200)
    full_name = serializers.SerializerMethodField(source="get_full_name")

    def get_full_name(self, obj):
        if not obj:
            return ""
        return obj.get_full_name()


class CargoAreaPersonSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="persona.id", read_only=True)
    user_id = serializers.IntegerField(source="persona.user.id", read_only=True)
    user = serializers.CharField(source="persona.user.username", max_length=200)
    numero_documento = serializers.CharField(
        source="persona.numero_documento", max_length=200
    )
    full_name = serializers.SerializerMethodField(source="get_full_name")

    def get_full_name(self, obj):
        if not obj:
            return ""
        return obj.persona.get_full_name()


class CargoAreaSerializer(serializers.ModelSerializer):
    area = AreaSerializer()

    class Meta:
        model = CargoArea
        fields = "__all__"


class PersonaSerializerFilter(serializers.Serializer):
    id = serializers.IntegerField()
    nombres = serializers.CharField()
    apellido_paterno = serializers.CharField()
    apellido_materno = serializers.CharField()
    numero_documento = serializers.CharField()
    correo = serializers.CharField()
    celular = serializers.CharField()


class PeridoExpedienteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()
    is_active = serializers.BooleanField()
    is_active_matricula = serializers.BooleanField()
