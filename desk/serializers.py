from rest_framework import serializers

from desk.models import (
    Headquarter,
    Procedure,
    Procedure_ProcReq,
    ProcedureRequirement,
    ProcedureType,
)


class HeadquarterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Headquarter
        fields = "__all__"


class ProcedureRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedureRequirement
        fields = "__all__"


class ProcedureTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedureType
        fields = "__all__"


class Procedure_ProcReqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure_ProcReq
        fields = "__all__"


class ProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure
        fields = "__all__"
