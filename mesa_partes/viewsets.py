from rest_framework.viewsets import ModelViewSet
from mesa_partes.models import *
from mesa_partes.serializers import *
# from rest_framework.permissions import IsAuthenticated


class TramiteViewSet(ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    queryset = Tramite.objects.all()
    serializer_class = TramiteSerializer
