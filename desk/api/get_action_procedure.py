from rest_framework.response import Response
from rest_framework import status
from desk.models import procedureAction
from desk.serializers import ProcedureActionSerializer


def api_get_action_procedure(request):
    try:
        action = procedureAction.objects.filter(is_active=True)
        serializer_action = ProcedureActionSerializer(action, many=True)
        return Response(
            {
                "actions": serializer_action.data,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
