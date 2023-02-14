from rest_framework import serializers
from core.models import *


class PeriodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periodo
        fields = '__all__'


class EtapaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etapa
        fields = '__all__'


class MenuSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=200)
    url = serializers.CharField(max_length=200)
    icon = serializers.CharField(max_length=200)
    app = serializers.SerializerMethodField(source="get_app")

    def get_app(self, obj):
        return obj.app.name

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = '__all__'

class PersonListSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        nombres = serializers.CharField(max_length=200)
        apellido_paterno = serializers.CharField(max_length=200)
        apellido_materno = serializers.CharField(max_length=200)
        numero_documento = serializers.CharField(max_length=200)