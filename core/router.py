from rest_framework.routers import DefaultRouter

from core.viewsets import PersonaViewSet

router = DefaultRouter()


router.register("persona", PersonaViewSet)
