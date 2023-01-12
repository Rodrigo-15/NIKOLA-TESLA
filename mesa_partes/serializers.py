from rest_framework import serializers

from core.models import Persona
from .models import RequisitoTramite, Tramite


class TramiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tramite
        fields = '__all__'


class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = '__all__'


class RequisitoTramiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequisitoTramite
        fields = '__all__'
