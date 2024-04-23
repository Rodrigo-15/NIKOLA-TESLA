from rest_framework import serializers
from desk.models import ProcedureRequirement


class ProcedureRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedureRequirement
        fields = "__all__"
