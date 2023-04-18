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