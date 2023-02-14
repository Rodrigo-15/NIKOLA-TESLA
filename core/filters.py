#django filter
from core.models import *
from core.serializers import *
import django_filters.rest_framework
from rest_framework import generics

class PersonListFilter (generics.ListAPIView):
    queryset = Persona.objects.all()
    serializer_class = PersonListSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('nombres', 'apellido_paterno', 'apellido_materno', 'numero_documento')