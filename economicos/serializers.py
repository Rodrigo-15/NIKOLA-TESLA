from decimal import Clamped
from .models import *
from rest_framework.serializers import ModelSerializer
from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin,     
)

from rest_framework import serializers 

# conceptos
class ConceptoSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = Concepto
        fields = "__all__"
        list_serializer_class = BulkListSerializer     

# pagos
class PagoSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = Pago
        fields = "__all__"
        list_serializer_class = BulkListSerializer



class PagoSerializerFilter(serializers.Serializer):
    id = serializers.IntegerField()
    nombre_cliente = serializers.CharField()    
    numero_documento = serializers.CharField()
    numero_operacion = serializers.CharField()
    fecha_operacion = serializers.DateField()     
    monto = serializers.DecimalField(max_digits=10, decimal_places=2)     
    is_active = serializers.BooleanField()
    concepto = serializers.IntegerField(source="concepto.id")
    concepto_nombre = serializers.CharField(source="concepto.nombre")
    expendiente = serializers.SerializerMethodField(source="get_expendiente")
    is_conciliado = serializers.BooleanField()     
    is_validado = serializers.BooleanField()
    adjunto = serializers.CharField()
    
    def get_expendiente(self, obj):
        return obj.expendiente.id if obj.expendiente else None   



