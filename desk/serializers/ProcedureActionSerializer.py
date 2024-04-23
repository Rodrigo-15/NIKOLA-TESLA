from rest_framework import serializers
from desk.models import procedureAction


class ProcedureActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = procedureAction
        fields = "__all__"
