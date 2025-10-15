from rest_framework import routers
from .views import (
    ProgramaViewSet, FacultadViewSet, CursosViewSet,
    DocenteViewSet, HorarioViewSet, MatriculaViewSet
)

router = routers.DefaultRouter()
router.register(r'programas', ProgramaViewSet)
router.register(r'facultades', FacultadViewSet)
router.register(r'cursos', CursosViewSet)
router.register(r'docentes', DocenteViewSet)
router.register(r'horarios', HorarioViewSet)
router.register(r'matriculas', MatriculaViewSet)

urlpatterns = router.urls
