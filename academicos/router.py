from rest_framework.routers import DefaultRouter
from academicos.viewsets import *

router = DefaultRouter()

router.register("programa", ProgramaViewSet)
router.register("cursos", CursosViewSet)
router.register("docente", DocenteViewSet)
router.register("horario", HorarioViewSet)
router.register("matricula", MatriculaViewSet)


from rest_framework_bulk.routes import BulkRouter
router_bulk = BulkRouter()
router_bulk.register("matricula_bulk", MatriculaBulkViewSet, "matricula")