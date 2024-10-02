from rest_framework.response import Response
from rest_framework import status
from desk.models import Procedure_ProcReq, ProcedureRequirement


def api_get_procedures_requirements(request):
    try:
        procedure_type_id = request.data["procedure_type_id"]
        requirements = Procedure_ProcReq.objects.filter(
            procedure_type_id=procedure_type_id, is_active=True
        )
        obj_requirements = []
        for r in requirements:
            requirement = ProcedureRequirement.objects.filter(
                id=r.requirement_id
            ).values("id", "description")
            obj_requirements.append(requirement[0])
        return Response(obj_requirements)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
