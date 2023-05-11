from rest_framework.viewsets import ModelViewSet

from core.models import *
from core.serializers import *


class PersonaViewSet(ModelViewSet):
    queryset = Persona.objects.all()
    serializer_class = PersonSerializer


class AreaViewSet(ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer