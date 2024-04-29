from rest_framework import serializers
from desk.models import Procedure


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
