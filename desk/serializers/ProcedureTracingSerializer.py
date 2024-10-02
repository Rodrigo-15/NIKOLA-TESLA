from rest_framework import serializers
from desk.models import ProcedureTracing

class ProcedureTracingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedureTracing
        fields = "__all__"


