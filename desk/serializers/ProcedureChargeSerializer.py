from rest_framework import serializers
from core.models import Persona


class ProcedureChargeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    correlative = serializers.CharField()
    user_id = serializers.IntegerField()
    user_name = serializers.SerializerMethodField(source="get_user_name")
    created_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S %p")

    def get_user_name(self, obj):
        person = Persona.objects.filter(user_id=obj.user_id).first()
        if person:
            return person.get_full_name()
        return ""
