from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from academicos.models import Programa, Facultad, Cursos, Docente, Horario, Matricula
from .serializers import (
    ProgramaSerializer, FacultadSerializer, CursosSerializer,
    DocenteSerializer, HorarioSerializer, MatriculaSerializer
)

class ProgramaViewSet(viewsets.ModelViewSet):
    queryset = Programa.objects.all()
    serializer_class = ProgramaSerializer


class FacultadViewSet(viewsets.ModelViewSet):
    queryset = Facultad.objects.all()
    serializer_class = FacultadSerializer


class CursosViewSet(viewsets.ModelViewSet):
    queryset = Cursos.objects.all()
    serializer_class = CursosSerializer


class DocenteViewSet(viewsets.ModelViewSet):
    queryset = Docente.objects.all()
    serializer_class = DocenteSerializer


class HorarioViewSet(viewsets.ModelViewSet):
    queryset = Horario.objects.all()
    serializer_class = HorarioSerializer


class MatriculaViewSet(viewsets.ModelViewSet):
    queryset = Matricula.objects.all()
    serializer_class = MatriculaSerializer
