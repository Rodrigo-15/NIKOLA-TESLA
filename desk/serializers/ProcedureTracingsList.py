from rest_framework import serializers
from desk.models import ProcedureTracing, Procedure, procedureAction
from core.models import Area, Persona


class ProcedureTracingsList(serializers.Serializer):
    id = serializers.IntegerField()
    procedure_id = serializers.IntegerField()
    code_number = serializers.SerializerMethodField(source="get_code_number")
    action_id = serializers.IntegerField()
    action_name = serializers.SerializerMethodField(source="get_action_name")
    action_description = serializers.CharField()
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

    def get_action_name(self, obj):
        if obj.action_id:
            act = procedureAction.objects.filter(id=obj.action_id).first()
            return act.action
        return "No registrado"
