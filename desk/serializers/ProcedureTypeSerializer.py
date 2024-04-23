from rest_framework import serializers
from desk.models import ProcedureType


class ProcedureTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedureType
        fields = "__all__"
