from rest_framework import serializers
from desk.models import Procedure_ProcReq


class Procedure_ProcReqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure_ProcReq
        fields = "__all__"
