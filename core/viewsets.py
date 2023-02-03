from rest_framework.viewsets import ModelViewSet

from core.models import Persona
from core.serializers import PersonSerializer


class PersonaViewSet(ModelViewSet):
    queryset = Persona.objects.all()
    serializer_class = PersonSerializer
