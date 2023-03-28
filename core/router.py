from rest_framework.routers import DefaultRouter

from core.viewsets import PersonaViewSet , AreaViewSet

router = DefaultRouter()


router.register("persona", PersonaViewSet)
router.register("area", AreaViewSet)
