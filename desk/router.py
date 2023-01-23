from rest_framework.routers import DefaultRouter

from desk.viewsets import (
    HeadquarterViewSet,
    Procedure_ProcReqViewSet,
    ProcedureRequirementViewSet,
    ProcedureTypeViewSet,
    ProcedureViewSet,
)

router = DefaultRouter()

router.register("headquarters", HeadquarterViewSet)
router.register("procedure_requirement", ProcedureRequirementViewSet)
router.register("procedure_type", ProcedureTypeViewSet)
router.register("procedure_procreqs", Procedure_ProcReqViewSet)
router.register("procedures", ProcedureViewSet)
