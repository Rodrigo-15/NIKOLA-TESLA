from rest_framework import serializers


class ProcedureFilesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    file = serializers.FileField()
    procedure_id = serializers.IntegerField()
    file_name = serializers.SerializerMethodField(source="get_file_name")
    created_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S %p")

    def get_file_name(self, obj):
        return obj.file.name.split("/")[-1]
