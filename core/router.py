from rest_framework.routers import DefaultRouter

from core.viewsets import PersonaViewSet , AreaViewSet, PersonaJuridicaViewSet

router = DefaultRouter()


router.register("persona", PersonaViewSet)
router.register("area", AreaViewSet)
router.register("persona_juridica", PersonaJuridicaViewSet)
