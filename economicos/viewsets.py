
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework_bulk import BulkModelViewSet
from rest_framework import filters


class ConceptoViewSet(BulkModelViewSet):
    #permission_classes = (IsAuthenticated,)
    queryset = Concepto.objects.all().order_by( "codigo","-is_active","id")
    serializer_class = ConceptoSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("nombre", "codigo", "precio")


class PagoViewSet(BulkModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Pago.objects.all().order_by("-fecha_operacion")
    serializer_class = PagoSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("nombre_cliente", "numero_operacion", "numero_documento")

