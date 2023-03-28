from rest_framework.viewsets import ModelViewSet

from core.models import *
from core.serializers import *
import django_filters.rest_framework
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend


class PersonaViewSet(ModelViewSet):
    queryset = Persona.objects.all()
    serializer_class = PersonSerializer


class AreaViewSet(ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer