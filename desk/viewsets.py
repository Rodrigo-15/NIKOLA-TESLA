from rest_framework.viewsets import ModelViewSet

from desk.models import (
    Headquarter,
    Procedure,
    Procedure_ProcReq,
    ProcedureRequirement,
    ProcedureTracing,
    ProcedureType,
)
from desk.serializers import (
    HeadquarterSerializer,
    Procedure_ProcReqSerializer,
    ProcedureRequirementSerializer,
    ProcedureSerializer,
    ProcedureTracingSerializer,
    ProcedureTypeSerializer,
)

# from rest_framework.permissions import IsAuthenticated


class HeadquarterViewSet(ModelViewSet):
    queryset = Headquarter.objects.all()
    serializer_class = HeadquarterSerializer


class ProcedureRequirementViewSet(ModelViewSet):
    queryset = ProcedureRequirement.objects.all()
    serializer_class = ProcedureRequirementSerializer


class ProcedureTypeViewSet(ModelViewSet):
    queryset = ProcedureType.objects.all()
    serializer_class = ProcedureTypeSerializer


class Procedure_ProcReqViewSet(ModelViewSet):
    queryset = Procedure_ProcReq.objects.all()
    serializer_class = Procedure_ProcReqSerializer


class ProcedureViewSet(ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    queryset = Procedure.objects.all()
    serializer_class = ProcedureSerializer

class ProcedureTracingViewSet(ModelViewSet):
    queryset = ProcedureTracing.objects.all()
    serializer_class = ProcedureTracingSerializer
