from rest_framework.response import Response
from rest_framework import status
from desk.models import Procedure
from desk.serializers import ProcedureSerializer


def api_get_procedure_by_id(request, procedure_id):
    try:
        procedure = Procedure.objects.filter(id=procedure_id).first()
        data = ProcedureSerializer(procedure).data
        return Response(data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
