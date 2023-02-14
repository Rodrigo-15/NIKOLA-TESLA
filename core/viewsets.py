from rest_framework.viewsets import ModelViewSet

from core.models import *
from core.serializers import *
import django_filters.rest_framework
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

class PersonaViewSet(ModelViewSet):
    queryset = Persona.objects.all()
    serializer_class = PersonSerializer


class PersonFilter(generics.ListAPIView):
    queryset = Persona.objects.all()[:10]
    serializer_class = PersonListSerializer
    filter_backends = (DjangoFilterBackend)
    filter_fields = (
        "nombres",
        "apellido_paterno",
        "apellido_materno",
        "numero_documento",
    )
