from rest_framework import serializers
from core.models import Persona
from desk.models import (
    Headquarter,
    Procedure,
    Procedure_ProcReq,
    ProcedureRequirement,
    ProcedureTracing,
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
    created_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S")
    
    class Meta:
        model = Procedure
        fields = "__all__"


class ProcedureTracingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedureTracing
        fields = "__all__"


class ProcedureTracingsList(serializers.Serializer):
    id = serializers.IntegerField()
    action = serializers.CharField()
    action_log = serializers.CharField()
    is_finished = serializers.BooleanField()
    is_approved = serializers.BooleanField()
    user = serializers.SerializerMethodField(source="get_user")
    date = serializers.SerializerMethodField(source="get_date")
    hour = serializers.SerializerMethodField(source="get_hour")

    def get_date(self, obj):
        return obj.created_at.strftime("%d/%m/%Y")

    def get_hour(self, obj):
        return obj.created_at.strftime("%H:%M:%S")

    def get_user(self, obj):
        person = Persona.objects.filter(user_id=obj.user_id).first()
        if person:
            print(person.nombres)
            return (
                person.nombres
                + " "
                + person.apellido_paterno
                + " "
                + person.apellido_materno
            )

        return obj.user.username
