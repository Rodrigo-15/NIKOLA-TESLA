from rest_framework.viewsets import ModelViewSet
from academicos.models import *
from academicos.serializers import  *
from rest_framework.permissions import IsAuthenticated

class ProgramaViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Programa.objects.all()
    serializer_class = ProgramaSerializer

# cursos, docente, horario, matricula
class CursosViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Cursos.objects.all()
    serializer_class = CursosSerializer


class DocenteViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Docente.objects.all()
    serializer_class = DocenteSerializer


class HorarioViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Horario.objects.all()
    serializer_class = HorarioSerializer


class MatriculaViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Matricula.objects.all()
    serializer_class = MatriculaSerializer
    


from rest_framework_bulk import (
    BulkModelViewSet,
)



from core.models import Periodo
from rest_framework.response import Response
class MatriculaBulkViewSet(BulkModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Matricula.objects.all()
    serializer_class = MatriculaBulkSerializer