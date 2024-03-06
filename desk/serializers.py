from rest_framework import serializers
from core.models import Persona, Area, PersonaJuridica
from desk.models import (
    Headquarter,
    Procedure,
    Procedure_ProcReq,
    ProcedureRequirement,
    ProcedureTracing,
    ProcedureType,
    Anexo,
    ProcedureCharge,
)
from django.db.models import Count


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
    area_id = serializers.SerializerMethodField(source="get_area_id")
    person_full_name = serializers.SerializerMethodField(source="get_person_full_name")
    person_document = serializers.SerializerMethodField(source="get_person_document")
    code_number = serializers.CharField()
    procedure_type_id = serializers.IntegerField()
    procedure_type_description = serializers.SerializerMethodField(
        source="get_procedure_type_description"
    )
    subject = serializers.CharField()
    description = serializers.CharField()
    attached_files = serializers.FileField()
    reference_doc_number = serializers.CharField()
    headquarter_id = serializers.IntegerField()
    headquarter_name = serializers.SerializerMethodField(source="get_headquarter_name")
    user_id = serializers.IntegerField()
    user_name = serializers.SerializerMethodField(source="get_user_name")
    created_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S %p")
    updated_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S %p")
    type_person = serializers.SerializerMethodField(source="get_type_person")
    state = serializers.SerializerMethodField(source="get_state")

    def get_user_name(self, obj):
        person = Persona.objects.filter(user_id=obj.user_id).first()
        if person:
            return person.get_full_name()
        return None

    def get_headquarter_name(self, obj):
        headquarter = Headquarter.objects.filter(id=obj.headquarter_id).first()
        if headquarter:
            return headquarter.name
        return None

    def get_procedure_type_description(self, obj):
        procedure_type = ProcedureType.objects.filter(id=obj.procedure_type_id).first()
        if procedure_type:
            return procedure_type.description
        return None

    def get_person_document(self, obj):
        person = Persona.objects.filter(id=obj.file.person_id).first()
        if person:
            return person.numero_documento

        return None

    def get_person_full_name(self, obj):
        file = obj.file
        if file.person_id is None and file.legalperson_id is None:
            area = Area.objects.filter(id=file.area_id).first()
            return area.nombre
        elif file.area_id is None and file.legalperson_id is None:
            person = Persona.objects.filter(id=file.person_id).first()
            return person.get_full_name()
        elif file.area_id is None and file.person_id is None:
            legal_person = PersonaJuridica.objects.filter(
                id=file.legalperson_id
            ).first()
            return legal_person.razon_social
        else:
            return "No registrado"

    def get_person_id(self, obj):
        if obj.file.person_id:
            return obj.file.person_id
        elif obj.file.legalperson_id:
            return obj.file.legalperson_id
        return None

    def get_type_person(self, obj):
        if obj.file.person_id:
            return 1
        elif obj.file.legalperson_id:
            return 2
        elif obj.file.area_id:
            return 0
        return None

    def get_area_id(self, obj):
        if obj.file.area_id:
            return obj.file.area_id
        return None

    def get_attached_file(self, obj):
        if obj.attached_files:
            return obj.attached_files.url
        return "No adjunto"

    def get_state(self, obj):
        if ProcedureTracing.objects.filter(procedure_id=obj.id).count() == 1:
            return "Iniciado"
        elif ProcedureTracing.objects.filter(procedure_id=obj.id).last().is_archived:
            return "Archivado"
        elif ProcedureTracing.objects.filter(procedure_id=obj.id).last().is_finished:
            return "Concluido"
        return "En proceso"

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
    code_number = serializers.SerializerMethodField(source="get_code_number")
    action = serializers.CharField()
    action_log = serializers.CharField()
    is_finished = serializers.BooleanField()
    is_approved = serializers.BooleanField()
    user_id = serializers.IntegerField()
    user = serializers.SerializerMethodField(source="get_user")
    assigned_user_id = serializers.IntegerField()
    assigned_user = serializers.SerializerMethodField(source="get_assigned_user")
    date = serializers.SerializerMethodField(source="get_date")
    hour = serializers.SerializerMethodField(source="get_hour")
    area_name = serializers.SerializerMethodField(source="get_area_name")
    estate = serializers.SerializerMethodField(source="get_estate")
    document_response = serializers.FileField()

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
            person = Persona.objects.filter(user_id=obj.assigned_user_id).first()
            if not person:
                return "No Asignado"

            return (
                person.nombres
                + " "
                + person.apellido_paterno
                + " "
                + person.apellido_materno
            )

        return "No Asignado"

    def get_code_number(self, obj):
        procedure = Procedure.objects.filter(id=obj.procedure_id).first()
        if procedure:
            return procedure.code_number
        return ""

    def get_area_name(self, obj):
        area = Area.objects.filter(id=obj.from_area_id).first()
        if area:
            return area.nombre
        return "No Asignado"

    def get_area_name(self, obj):
        area = Area.objects.filter(id=obj.from_area_id).first()
        if area:
            return area.nombre
        return "No Asignado"

    def get_estate(self, obj):
        # si es el primer registro de trazabilidad poner el estado en Iniciado si no poner en proceso
        data = (
            ProcedureTracing.objects.filter(procedure_id=obj.procedure_id)
            .order_by("created_at")
            .first()
        )
        if data.id == obj.id:
            return "Iniciado"
        elif obj.is_finished:
            return "Concluido"
        return "En proceso"


class ProcedureListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code_number = serializers.CharField()
    created_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S %p")
    updated_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S %p")
    reference_doc_number = serializers.CharField()
    subject = serializers.CharField()
    person_full_name = serializers.SerializerMethodField(source="get_person_full_name")
    last_action = serializers.SerializerMethodField(source="get_last_action")
    state = serializers.SerializerMethodField(source="get_state")
    number_of_sheets = serializers.IntegerField()
    area_id = serializers.SerializerMethodField(source="get_area_id")

    def get_person_full_name(self, obj):
        file = obj.file
        if file.person_id is None and file.legalperson_id is None:
            area = Area.objects.filter(id=file.area_id).first()
            return area.nombre
        elif file.area_id is None and file.legalperson_id is None:
            person = Persona.objects.filter(id=file.person_id).first()
            return person.get_full_name()

        elif file.area_id is None and file.person_id is None:
            legal_person = PersonaJuridica.objects.filter(
                id=file.legalperson_id
            ).first()
            return legal_person.razon_social

        else:
            return "No registrado"

    def get_last_action(self, obj):
        procedure_tracing = (
            ProcedureTracing.objects.filter(procedure_id=obj.id)
            .order_by("-created_at")
            .first()
        )
        if procedure_tracing:
            return procedure_tracing.action_log
        return "No registrado"

    def get_state(self, obj):
        if ProcedureTracing.objects.filter(procedure_id=obj.id).count() == 1:
            return "Iniciado"
        elif ProcedureTracing.objects.filter(procedure_id=obj.id).last().is_archived:
            return "Archivado"
        elif ProcedureTracing.objects.filter(procedure_id=obj.id).last().is_finished:
            return "Concluido"
        return "En proceso"

    def get_area_id(self, obj):
        if obj.file.area_id:
            return obj.file.area_id
        return None


class AnexoListSerializer(serializers.Serializer):
    procedure_id = serializers.SerializerMethodField(source="get_procedure_id")
    code_number = serializers.SerializerMethodField(source="get_code_number")
    subject = serializers.SerializerMethodField(source="get_subject")
    description = serializers.SerializerMethodField(source="get_description")
    creat_at = serializers.SerializerMethodField(source="get_creat_at")

    def get_procedure_id(self, obj):
        procedure = Procedure.objects.filter(id=obj.procedure_anexo_id).first()
        if procedure:
            return procedure.id
        return ""

    def get_code_number(self, obj):
        procedure = Procedure.objects.filter(id=obj.procedure_anexo_id).first()
        if procedure:
            return procedure.code_number
        return ""

    def get_subject(self, obj):
        procedure = Procedure.objects.filter(id=obj.procedure_anexo_id).first()
        if procedure:
            return procedure.subject
        return ""

    def get_description(self, obj):
        procedure = Procedure.objects.filter(id=obj.procedure_anexo_id).first()
        if procedure:
            return procedure.description
        return ""

    def get_creat_at(self, obj):
        procedure = Procedure.objects.filter(id=obj.procedure_anexo_id).first()
        if procedure:
            return procedure.created_at.strftime("%d/%m/%Y %H:%M:%S %p")
        return ""


class ProcedureChargeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    correlative = serializers.CharField()
    area_id = serializers.IntegerField()
    area_name = serializers.SerializerMethodField(source="get_area_name")
    user_id = serializers.IntegerField()
    user_name = serializers.SerializerMethodField(source="get_user_name")
    created_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S %p")
    path_file = serializers.CharField()

    def get_area_name(self, obj):
        area = Area.objects.filter(id=obj.area_id).first()
        if area:
            return area.nombre
        return ""

    def get_user_name(self, obj):
        person = Persona.objects.filter(user_id=obj.user_id).first()
        if person:
            return person.get_full_name()
        return ""
