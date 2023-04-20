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
    id = serializers.IntegerField()
    file_id = serializers.IntegerField()
    person_id = serializers.SerializerMethodField(source="get_person_id")
    person_full_name = serializers.SerializerMethodField(source="get_person_full_name")
    person_document = serializers.SerializerMethodField(
        source="get_person_document")
    code_number = serializers.CharField()
    procedure_type_id = serializers.IntegerField()
    procedure_type_description = serializers.SerializerMethodField(
        source="get_procedure_type_description")
    subject = serializers.CharField()
    description = serializers.CharField()
    reference_doc_number = serializers.CharField()
    headquarter_id = serializers.IntegerField()
    headquarter_name = serializers.SerializerMethodField(
        source="get_headquarter_name")
    user_id = serializers.IntegerField()
    user_name = serializers.SerializerMethodField(source="get_user_name")
    created_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S %p")
    updated_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S %p")
    state = serializers.SerializerMethodField(source="get_state")

    def get_user_name(self, obj):
        person = Persona.objects.filter(user_id=obj.user_id).first()
        if person:
            return person.get_full_name()
        return None

    def get_headquarter_name(self, obj):
        headquarter = Headquarter.objects.filter(
            id=obj.headquarter_id).first()
        if headquarter:
            return headquarter.name
        return None

    def get_procedure_type_description(self, obj):
        procedure_type = ProcedureType.objects.filter(
            id=obj.procedure_type_id).first()
        if procedure_type:
            return procedure_type.description
        return None

    def get_person_document(self, obj):
        person = Persona.objects.filter(id=obj.file.person_id).first()
        if person:
            return person.numero_documento

        return None

    def get_person_full_name(self, obj):
        person = Persona.objects.filter(id=obj.file.person_id).first()
        if person:
            return person.get_full_name()
        return None

    def get_person_id(self, obj):
        person = Persona.objects.filter(id=obj.file.person_id).first()
        if person:
            return person.id

        return None
    
    def get_state(self, obj):
        procedure_tracing = ProcedureTracing.objects.filter(
             is_approved=False, procedure_id=obj.id ).exclude(to_area_id = None).first()
        if procedure_tracing:
            return True
        return False

    class Meta:
        model = Procedure
        fields = "__all__"


class ProcedureTracingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedureTracing
        fields = "__all__"


class ProcedureTracingsList(serializers.Serializer):
    id = serializers.IntegerField()
    procedure_id = serializers.IntegerField()
    action = serializers.CharField()
    action_log = serializers.CharField()
    is_finished = serializers.BooleanField()
    is_approved = serializers.BooleanField()
    user_id = serializers.IntegerField()
    user = serializers.SerializerMethodField(source="get_user")
    assigned_user_id = serializers.IntegerField()
    assigned_user = serializers.SerializerMethodField(
        source="get_assigned_user")
    date = serializers.SerializerMethodField(source="get_date")
    hour = serializers.SerializerMethodField(source="get_hour")

    def get_date(self, obj):
        return obj.created_at.strftime("%d/%m/%Y")

    def get_hour(self, obj):
        return obj.created_at.strftime("%H:%M:%S %p")

    def get_user(self, obj):
        person = Persona.objects.filter(user_id=obj.user_id).first()
        if person:
            return (
                person.nombres
                + " "
                + person.apellido_paterno
                + " "
                + person.apellido_materno
            )

        return obj.user.username

    def get_assigned_user(self, obj):
        if obj.assigned_user_id:
            person = Persona.objects.filter(
                user_id=obj.assigned_user_id).first()
            if not person:
                return 'No Asignado'

            return (
                person.nombres
                + " "
                + person.apellido_paterno
                + " "
                + person.apellido_materno
            )

        return 'No Asignado'


class ProcedureListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code_number = serializers.CharField()
    created_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S %p")
    updated_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S %p")
    reference_doc_number = serializers.CharField()
    subject = serializers.CharField()
    solicitante = serializers.SerializerMethodField(source="get_solicitante")
    last_action = serializers.SerializerMethodField(source="get_last_action")
    state = serializers.SerializerMethodField(source="get_state")

    def get_solicitante(self, obj):
        file = obj.file
        person = Persona.objects.filter(user_id=file.person.user_id).first()
        if person:
            return person.get_full_name()
        return "No registrado"

    def get_last_action(self, obj):
        procedure_tracing = ProcedureTracing.objects.filter(
            procedure_id=obj.id).order_by("-created_at").first()
        if procedure_tracing:
            return procedure_tracing.action
        return "No registrado"

    def get_state(self, obj):
        procedure_tracing = ProcedureTracing.objects.filter(
             is_approved=False, procedure_id=obj.id ).exclude(to_area_id = None).first()
        if procedure_tracing:
            return True
        return False
    