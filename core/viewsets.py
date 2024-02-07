from rest_framework.viewsets import ModelViewSet

from core.models import *
from core.serializers import *
from rest_framework.response import Response


class PersonaViewSet(ModelViewSet):
    queryset = Persona.objects.all()
    serializer_class = PersonSerializer

class AreaViewSet(ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer

class PersonaJuridicaViewSet(ModelViewSet):
    queryset = persona_juridica.objects.all()
    serializer_class = PersonaJuridicaSerializer